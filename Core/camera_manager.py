import cv2
import time
import re


class CameraManager:
    """Camera detection and management"""
    @staticmethod
    def detect_cameras():
        available = []
        print("Detecting available cameras...")
        
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                backend = cap.getBackendName()
                ret, _ = cap.read()
                
                if ret:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    camera_name = f"📹 {'Default' if i == 0 else f'Camera {i}'} ({width}x{height})"
                    
                    available.append({
                        "index": i,
                        "name": camera_name,
                        "backend": backend,
                        "resolution": f"{width}x{height}"
                    })
                    print(f"✅ Found: {camera_name} [{backend}]")
                
                cap.release()
            time.sleep(0.1)
        
        if not available:
            print("⚠️ No cameras detected")
            available.append({
                "index": 0,
                "name": "📹 Default Camera (Not detected)",
                "backend": "unknown",
                "resolution": "unknown"
            })
        
        return available
    
    @staticmethod
    def validate_ip(ip):
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        try:
            return all(0 <= int(part) <= 255 for part in ip.split('.'))
        except:
            return False