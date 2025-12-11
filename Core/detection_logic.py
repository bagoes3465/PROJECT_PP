"""Detection Logic and Processing"""
import cv2
import numpy as np
import datetime
import time
import os
from Core.constants import REJECTED_IMAGES_FOLDER
from Core.utils import ambil_keputusan


class DetectionProcessor:
    """Handle detection processing and decision making"""
    
    def __init__(self, config, model_manager, tracker, serial_manager):
        self.config = config
        self.model_manager = model_manager
        self.tracker = tracker
        self.serial_manager = serial_manager
        
        self.processed_objects = {}
        self.last_decision_time = 0
        self.inference_time = 0
    
    def is_in_detection_zone(self, centroid_x):
        """Check if object is in detection zone"""
        zone_start = self.config.detection_zone_x - self.config.detection_zone_tolerance
        zone_end = self.config.detection_zone_x + self.config.detection_zone_tolerance
        return zone_start <= centroid_x <= zone_end
    
    def should_make_decision(self, object_id, current_time):
        """Check if we should make a decision for this object"""
        if object_id in self.processed_objects:
            return False
        
        if current_time - self.last_decision_time < self.config.decision_cooldown:
            return False
        
        return True
    
    def process_frame(self, frame):
        """
        Process a single frame with YOLO detection and tracking
        
        Returns:
            dict: {
                'frame_result': annotated frame,
                'decision_info': decision information if made,
                'objects': tracked objects,
                'inference_time': inference time in ms
            }
        """
        start_time = time.time()
        
        # Run YOLO detection
        results = self.model_manager.predict(frame, self.config.min_conf, self.config.device)
        self.inference_time = (time.time() - start_time) * 1000
        
        # Extract boxes
        boxes = results[0].boxes
        filtered_boxes = boxes[boxes.conf > self.config.min_conf]
        
        # Prepare rectangles and labels for tracking
        rects = []
        labels_dict = {}
        
        for idx, box in enumerate(filtered_boxes.xyxy):
            x1, y1, x2, y2 = map(int, box)
            rects.append((x1, y1, x2, y2))
            
            cls_id = int(filtered_boxes.cls[idx])
            label = self.model_manager.model.names[cls_id]
            conf = float(filtered_boxes.conf[idx])
            labels_dict[idx] = {"label": label, "conf": conf}
        
        # Update tracker
        objects = self.tracker.update(rects)
        
        # Build centroids for mapping
        input_centroids = []
        for (startX, startY, endX, endY) in rects:
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            input_centroids.append((cX, cY))
        
        if input_centroids:
            input_centroids = np.array(input_centroids)
        else:
            input_centroids = np.array([])
        
        # Annotate frame
        frame_result = results[0].plot()
        current_time = time.time()
        
        decision_info = None
        
        # Process tracked objects
        for object_id, centroid in objects.items():
            cx, cy = centroid
            
            # Draw tracking info
            cv2.circle(frame_result, (cx, cy), 4, (0, 255, 0), -1)
            cv2.putText(frame_result, f"ID:{object_id}", (cx - 10, cy - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Check if in detection zone
            if self.is_in_detection_zone(cx):
                cv2.circle(frame_result, (cx, cy), 8, (0, 255, 255), 2)
                
                should_decide = self.should_make_decision(object_id, current_time)
                
                # Map to nearest detection
                mapped_idx = None
                if input_centroids.size != 0:
                    dists = np.linalg.norm(input_centroids - np.array([cx, cy]), axis=1)
                    best_idx = int(dists.argmin())
                    if dists[best_idx] <= self.tracker.maxDistance:
                        mapped_idx = best_idx
                
                if mapped_idx is None and labels_dict:
                    mapped_idx = max(labels_dict.keys(), 
                                   key=lambda k: labels_dict[k].get("conf", 0.0))
                
                # Make decision
                if should_decide and mapped_idx is not None:
                    object_labels = [labels_dict[mapped_idx]["label"]]
                    keputusan = ambil_keputusan(object_labels)
                    
                    self.processed_objects[object_id] = {
                        "decision": keputusan,
                        "time": current_time,
                        "labels": object_labels
                    }
                    self.last_decision_time = current_time
                    
                    # Send to serial
                    if self.serial_manager.connected:
                        self.serial_manager.send_decision(keputusan)
                    
                    decision_info = {
                        "keputusan": keputusan,
                        "labels": object_labels,
                        "object_id": object_id,
                        "centroid": (cx, cy),
                        "confidence": labels_dict[mapped_idx]["conf"]
                    }
                    
                    print(f"🎯 Decision: ID {object_id} = {keputusan} at X={cx}")
        
        # Draw detection zone
        self._draw_detection_zone(frame_result)
        
        # Cleanup old objects
        self.cleanup_old_objects(current_time)
        
        return {
            'frame_result': frame_result,
            'decision_info': decision_info,
            'objects': objects,
            'inference_time': self.inference_time
        }
    
    def _draw_detection_zone(self, frame):
        """Draw detection zone on frame"""
        zone_x = self.config.detection_zone_x
        cv2.line(frame, (zone_x, 0), (zone_x, frame.shape[0]), (0, 255, 255), 2)
        cv2.putText(frame, "DETECTION ZONE", (zone_x - 70, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        zone_start = zone_x - self.config.detection_zone_tolerance
        zone_end = zone_x + self.config.detection_zone_tolerance
        cv2.line(frame, (zone_start, 0), (zone_start, frame.shape[0]), (255, 255, 0), 1)
        cv2.line(frame, (zone_end, 0), (zone_end, frame.shape[0]), (255, 255, 0), 1)
    
    def cleanup_old_objects(self, current_time):
        """Remove old processed objects from memory"""
        to_remove = []
        for obj_id, data in self.processed_objects.items():
            if current_time - data["time"] > 10:
                to_remove.append(obj_id)
        
        for obj_id in to_remove:
            del self.processed_objects[obj_id]
    
    def save_rejected_image(self, image_array, keputusan, object_id):
        """Save rejected egg image"""
        if keputusan == "REJECT":
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"REJECT_ID{object_id}_{timestamp}.jpg"
                filepath = os.path.join(REJECTED_IMAGES_FOLDER, filename)
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filepath, image_bgr)
                print(f"✅ Saved rejected image: {filename}")
                return filepath
            except Exception as e:
                print(f"Error saving rejected image: {e}")
        return None