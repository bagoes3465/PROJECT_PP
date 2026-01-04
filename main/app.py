"""
Egg Sorter Application - Main Entry Point
Complete modular version with integrated UI
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
from datetime import datetime
import os
from tkinter import filedialog, messagebox
import threading
import time
import gc

# Import custom modules
from Core.constants import *
from Core.config import Config
from Core.tracker import CentroidTracker
from Core.serial_manager import SerialManager
from Core.model_manager import ModelManager
from Core.camera_manager import CameraManager
from Core.log_manager import LogManager
from Training.training_manager import TrainingManager
from Core.detection_logic import DetectionProcessor
from Core.utils import setup_tcl_environment, create_directories, play_alert_sound
from Core.camera_processor import CameraProcessor

# Import UI components
from UI.ui_components import ToastNotification
from UI.ui_top_bar import TopBar
from UI.ui_detection_tab import DetectionTab
from UI.ui_camera_tab import CameraTab
from UI.ui_settings_tab import DetectionSettingsTab, ModelSettingsTab
from UI.ui_other_tabs import SerialTab, LogTab, ChartTab
from UI.ui_camera_enhancement_tab import CameraEnhancementTab

# Import training UI
try:
    from UI.ui_training_tab import TrainingTab
    TRAINING_UI_AVAILABLE = True
except:
    TRAINING_UI_AVAILABLE = False
    print("⚠️ Training UI not available")

# Setup environment
setup_tcl_environment()
create_directories()

# CustomTkinter settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class EggSorterApp(ctk.CTk):
    """Main Application Class"""
    
    def __init__(self):
        super().__init__()
        
        self.title(f"{EMOJI['egg']} Sortir Kualitas Telur Otomatis - Conveyor Mode")
        self.geometry("1600x900")
        
        # Initialize managers
        self.config = Config()
        self.model_manager = ModelManager()
        self.log_manager = LogManager()
        self.serial_manager = SerialManager()
        self.tracker = CentroidTracker(maxDisappeared=30, maxDistance=80)
        self.training_manager = TrainingManager()

        # Initialize camera processor
        self.camera_processor = CameraProcessor()
        
        # Load model
        if not self.model_manager.load():
            self.destroy()
            return
        
        # Initialize detection processor
        self.detection_processor = DetectionProcessor(
            self.config, 
            self.model_manager, 
            self.tracker, 
            self.serial_manager
        )
        
        # Initialize state
        self.init_state()
        
        # Load configuration and logs
        self.config.load()
        self.log_manager.load()
        self.rebuild_stats()
        
        # Setup UI
        self.setup_ui()
        
        # Bind keys
        self.bind("<Escape>", lambda e: self.stop_camera_feed() if self.camera_running else None)
        self.bind("<F5>", lambda e: self.refresh_log())
        
        # Start background tasks
        self.start_camera_detection()
        self.start_serial_detection()
    
    def init_state(self):
        """Initialize application state"""
        self.stats_lock = threading.Lock()
        self.reject_count = 0
        self.accept_count = 0
        self.stop_camera = False
        self.camera_running = False
        self.camera_source = "local"
        self.available_cameras = []
        self.local_camera_index = 0
        self.fps = 0
        self.frame_times = []
        self.last_frame_time = time.time()
        self.chart_data = {"timestamps": [], "accept": [], "reject": []}
        self.max_chart_points = 50
    
    def rebuild_stats(self):
        """Rebuild statistics from log"""
        logs = self.log_manager.log_deteksi
        accept = sum(1 for log in logs if log.get("keputusan") == "ACCEPT")
        reject = sum(1 for log in logs if log.get("keputusan") == "REJECT")
        
        with self.stats_lock:
            self.accept_count = accept
            self.reject_count = reject
        
        temp_accept = temp_reject = 0
        for log in logs[-self.max_chart_points:]:
            if log.get("keputusan") == "ACCEPT":
                temp_accept += 1
            elif log.get("keputusan") == "REJECT":
                temp_reject += 1
            
            self.chart_data["timestamps"].append(log.get("waktu", ""))
            self.chart_data["accept"].append(temp_accept)
            self.chart_data["reject"].append(temp_reject)

    def check_camera_running(self):
        """Check if camera is currently running"""
        return self.camera_running
    
    # ==================== UI SETUP ====================
    
    def setup_ui(self):
        """Setup main UI"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top bar
        self.top_bar = TopBar(self)
        
        # Main content
        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Tabview
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Setup tabs
        self.setup_tabs()
        
        # Update initial stats
        self.update_stats()
    
    def setup_tabs(self):
        """Setup all tabs"""
        # Detection tab
        self.detection_tab = DetectionTab(self.tabview, {
            'upload_image': self.upload_image,
            'start_camera': self.start_camera,
            'stop_camera': self.stop_camera_feed,
            'reset_data': self.reset_data
        })
        
        # Camera tab
        self.camera_tab = CameraTab(self.tabview, {
            'change_source': self.change_camera_source,
            'refresh_cameras': self.refresh_cameras
        }, self.config.ip_camera)
        
        # Camera Enhancement tab
        self.enhancement_tab = CameraEnhancementTab(
            self.tabview, 
            self.camera_processor,
            {'on_settings_change': self.on_enhancement_change}
        )

        # Detection settings tab
        self.detection_settings_tab = DetectionSettingsTab(self.tabview, self.config, {
            'update_conf': self.update_conf,
            'update_zone_x': self.update_zone_x,
            'update_tolerance': self.update_tolerance,
            'update_cooldown': self.update_cooldown
        })
        
        # Model settings tab
        self.model_settings_tab = ModelSettingsTab(self.tabview, self.config, self.model_manager, {
            'change_device': self.change_device,
            'toggle_log': self.toggle_log,
            'toggle_alert': self.toggle_alert,
            'toggle_sound': self.toggle_sound,
            'save_config': self.save_config_ui,
            'load_config': self.load_config_ui,
            'check_camera_running': self.check_camera_running  # ADD THIS LINE
        })
        
        # Serial tab
        self.serial_tab = SerialTab(self.tabview, self.config, {
            'refresh_ports': self.refresh_serial_ports,
            'connect': self.connect_serial,
            'disconnect': self.disconnect_serial,
            'test': self.test_serial
        })
        
        # Training tab (if available)
        if TRAINING_UI_AVAILABLE:
            self.training_tab = TrainingTab(self.tabview, self.training_manager, self.config)
        
        # Log tab
        self.log_tab = LogTab(self.tabview, {
            'refresh': self.refresh_log,
            'export': self.export_log,
            'clear': self.clear_logs
        })
        
        # Chart tab
        self.chart_tab = ChartTab(self.tabview)
        if self.chart_data["timestamps"]:
            self.update_live_chart()
    
    # ==================== CAMERA MANAGEMENT ====================
    
    def start_camera_detection(self):
        """Start camera detection in background"""
        threading.Thread(target=self._detect_cameras_worker, daemon=True).start()
    
    def _detect_cameras_worker(self):
        """Worker to detect cameras"""
        time.sleep(0.5)
        self.available_cameras = CameraManager.detect_cameras()
        self.after(0, self._update_camera_list)
    
    def _update_camera_list(self):
        """Update camera dropdown"""
        camera_names = [cam["name"] for cam in self.available_cameras]
        self.camera_tab.update_camera_list(camera_names)
    
    def refresh_cameras(self):
        """Refresh camera list"""
        self.camera_tab.set_detect_button_state("disabled", "⏳")
        
        def detect():
            self.available_cameras = CameraManager.detect_cameras()
            camera_names = [cam["name"] for cam in self.available_cameras]
            self.after(0, lambda: self.camera_tab.update_camera_list(camera_names))
            self.after(0, lambda: self.camera_tab.set_detect_button_state("normal", f"{EMOJI['search']}"))
            self.after(0, lambda: messagebox.showinfo("Info", 
                f"✅ Ditemukan {len(self.available_cameras)} kamera"))
        
        threading.Thread(target=detect, daemon=True).start()
    
    def change_camera_source(self, source):
        """Change camera source"""
        self.camera_source = source

    def on_enhancement_change(self):
    # Save settings to config if needed
        if hasattr(self.config, 'camera_enhancement'):
            self.config.camera_enhancement = self.camera_processor.get_settings_dict()
    
    def get_selected_camera_index(self):
        """Get selected camera index"""
        selected_name = self.camera_tab.get_selected_camera()
        for cam in self.available_cameras:
            if cam["name"] == selected_name:
                return cam["index"]
        return 0
    
    # ==================== SERIAL MANAGEMENT ====================
    
    def start_serial_detection(self):
        """Start serial port detection"""
        threading.Thread(target=self._detect_serial_worker, daemon=True).start()
    
    def _detect_serial_worker(self):
        """Worker to detect serial ports"""
        time.sleep(0.5)
        self.after(0, self.refresh_serial_ports)
    
    def refresh_serial_ports(self):
        """Refresh serial port list"""
        ports = self.serial_manager.list_ports()
        self.serial_tab.update_ports(ports)
    
    def connect_serial(self):
        """Connect to serial port"""
        selected = self.serial_tab.port_var.get()
        if "No Ports" in selected or "Not Connected" in selected:
            messagebox.showwarning("Warning", "Pilih port serial terlebih dahulu!")
            return
        
        port = selected.split(" - ")[0]
        baudrate = int(self.serial_tab.baudrate_var.get())
        
        if self.serial_manager.connect(port, baudrate):
            self.config.serial_port = port
            self.config.serial_baudrate = baudrate
            self.serial_tab.update_status(True)
            self.top_bar.update_serial_status(True)
            messagebox.showinfo("Success", f"✅ Connected to {port}")
        else:
            messagebox.showerror("Error", f"❌ Failed to connect to {port}")
    
    def disconnect_serial(self):
        """Disconnect serial"""
        if self.serial_manager.disconnect():
            self.serial_tab.update_status(False)
            self.top_bar.update_serial_status(False)
            messagebox.showinfo("Info", "Serial disconnected")
    
    def test_serial(self, decision):
        """Test serial command"""
        if not self.serial_manager.connected:
            messagebox.showwarning("Warning", "Serial belum terhubung!")
            return
        
        if self.serial_manager.send_decision(decision):
            messagebox.showinfo("Test Success", f"✅ Sent: {decision}")
        else:
            messagebox.showerror("Test Failed", "❌ Failed to send command")
    
    # ==================== SETTINGS CALLBACKS ====================
    
    def update_conf(self, value):
        self.config.min_conf = value
    
    def update_zone_x(self, value):
        self.config.detection_zone_x = int(value)
        self.detection_processor.config.detection_zone_x = int(value)
    
    def update_tolerance(self, value):
        self.config.detection_zone_tolerance = int(value)
        self.detection_processor.config.detection_zone_tolerance = int(value)
    
    def update_cooldown(self, value):
        self.config.decision_cooldown = value
        self.detection_processor.config.decision_cooldown = value
    
    def toggle_log(self):
        self.config.aktifkan_log = self.model_settings_tab.log_checkbox.get()
    
    def toggle_alert(self):
        self.config.alert_enabled = self.model_settings_tab.alert_checkbox.get()
    
    def toggle_sound(self):
        self.config.alert_sound_enabled = self.model_settings_tab.sound_checkbox.get()
    
    def change_device(self, value):
        """Change processing device"""
        try:
            # Test device
            test_img = np.zeros((640, 640, 3), dtype=np.uint8)
            self.model_manager.predict(test_img, 0.5, value)
            
            old_device = self.config.device
            self.config.device = value
            
            if value == "cuda":
                import torch
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                self.model_settings_tab.update_device_info(
                    f"🚀 {gpu_name} ({gpu_memory:.1f}GB)", "#2ecc71")
                messagebox.showinfo("Device Changed", 
                    f"Model sekarang menggunakan GPU:\n{gpu_name}")
            else:
                self.model_settings_tab.update_device_info("💻 Using: CPU", "gray")
                messagebox.showinfo("Device Changed", "Model sekarang menggunakan CPU")
        
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengubah device:\n{str(e)}")
            self.model_settings_tab.device_var.set(old_device)
            self.config.device = old_device
    
    def save_config_ui(self):
        """Save configuration"""
        self.config.ip_camera = self.camera_tab.get_ip_address()
        self.config.camera_enhancement = self.camera_processor.get_settings_dict()
        if self.config.save():
            messagebox.showinfo("Success", "✅ Configuration saved!")
        else:
            messagebox.showerror("Error", "❌ Failed to save configuration!")
    
    def load_config_ui(self):
        """Load configuration"""
        self.config.load()
        # Update UI with loaded config
        self.detection_settings_tab.conf_slider.set(self.config.min_conf)
        self.detection_settings_tab.zone_x_slider.set(self.config.detection_zone_x)
        self.detection_settings_tab.tolerance_slider.set(self.config.detection_zone_tolerance)
        self.detection_settings_tab.cooldown_slider.set(self.config.decision_cooldown)
        messagebox.showinfo("Success", "✅ Configuration loaded!")
        if hasattr(self.config, 'camera_enhancement') and self.config.camera_enhancement:
            self.camera_processor.load_settings_dict(self.config.camera_enhancement)
            self.enhancement_tab.update_ui_from_processor()
    
    # ==================== IMAGE UPLOAD ====================
    
    def upload_image(self):
        """Upload and process image"""
        try:
            file_path = filedialog.askopenfilename(
                title="Pilih Gambar",
                filetypes=[("Image files", "*.jpg *.jpeg *.png")]
            )
            if not file_path:
                return
            
            image = Image.open(file_path).convert("RGB")
            
            # Process detection
            start_time = time.time()
            results = self.model_manager.predict(np.array(image), self.config.min_conf, self.config.device)
            inference_time = (time.time() - start_time) * 1000
            
            boxes = results[0].boxes
            filtered_boxes = boxes[boxes.conf > self.config.min_conf]
            labels = [self.model_manager.model.names[int(cls)] for cls in filtered_boxes.cls]
            
            result_img = results[0].plot()
            result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
            
            from Core.utils import ambil_keputusan
            keputusan = ambil_keputusan(labels) if labels else "ACCEPT"
            
            # Display
            self.display_image(result_img)
            self.detection_tab.update_decision(keputusan)
            
            # Update stats
            self.update_counts(keputusan)
            self.update_stats()
            
            # Alert
            if keputusan == "REJECT" and self.config.alert_enabled:
                alert_msg = f"Telur REJECT terdeteksi!\nAlasan: {', '.join(labels)}"
                ToastNotification.show(self, alert_msg, "reject")
                if self.config.alert_sound_enabled:
                    play_alert_sound()
            
            # Update chart
            self.chart_data["timestamps"].append(datetime.now())
            with self.stats_lock:
                self.chart_data["accept"].append(self.accept_count)
                self.chart_data["reject"].append(self.reject_count)
            self.update_live_chart()
            
            # Save rejected image
            saved_path = self.detection_processor.save_rejected_image(result_img, keputusan, "upload")
            
            # Log
            if self.config.aktifkan_log:
                log_entry = {
                    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "sumber": "Upload Gambar",
                    "kelas_terdeteksi": ", ".join(labels) if labels else "Tidak ada",
                    "keputusan": keputusan,
                    "confidence": f"{max([float(c) for c in filtered_boxes.conf], default=0):.2f}",
                    "inference_time_ms": f"{inference_time:.1f}",
                    "saved_path": saved_path if saved_path else "N/A"
                }
                self.log_manager.add_entry(log_entry)
                self.log_manager.save_append([log_entry])
                self.refresh_log()
        
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")
    
    # ==================== CAMERA PROCESSING ====================
    
    def start_camera(self):
        """Start camera feed"""
        if self.camera_running:
            messagebox.showwarning("Warning", "Kamera sudah berjalan!")
            return
        
        if self.camera_source == "ip":
            self.config.ip_camera = self.camera_tab.get_ip_address()
            if not CameraManager.validate_ip(self.config.ip_camera):
                messagebox.showerror("Error", "IP kamera tidak valid!")
                return
        else:
            self.local_camera_index = self.get_selected_camera_index()
        
        # Reset tracker
        self.tracker = CentroidTracker(maxDisappeared=30, maxDistance=80)
        self.detection_processor.tracker = self.tracker
        self.detection_processor.processed_objects = {}
        self.detection_processor.last_decision_time = 0
        
        self.stop_camera = False
        self.camera_running = True
        self.detection_tab.set_camera_running(True)
        
        threading.Thread(target=self.camera_loop, daemon=True).start()
    
    def camera_loop(self):
        """Camera processing loop"""
        cap = None
        try:
            cap = self.open_camera()
            if not cap:
                return
            
            frame_count = 0
            
            while not self.stop_camera:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.5)
                    continue
                
                frame_count += 1
                self.calculate_fps()
                frame = self.camera_processor.process_frame(frame)
                
                # Process frame
                result = self.detection_processor.process_frame(frame)
                
                # Display
                frame_rgb = cv2.cvtColor(result['frame_result'], cv2.COLOR_BGR2RGB)
                self.display_image(frame_rgb)
                
                # Handle decision
                if result['decision_info']:
                    info = result['decision_info']
                    self.update_counts(info['keputusan'])
                    
                    # Alert
                    if info['keputusan'] == "REJECT" and self.config.alert_enabled:
                        alert_msg = f"REJECT! ID:{info['object_id']} | {', '.join(info['labels'])}"
                        self.after(0, lambda m=alert_msg: ToastNotification.show(self, m, "reject"))
                        if self.config.alert_sound_enabled:
                            play_alert_sound()
                    
                    # Update UI
                    self.after(0, lambda d=info['keputusan']: self.detection_tab.update_decision(d))
                    
                    # Save image
                    self.detection_processor.save_rejected_image(
                        frame_rgb, info['keputusan'], info['object_id']
                    )
                    
                    # Log
                    if self.config.aktifkan_log:
                        self.log_camera_detection(info)
                
                # Update stats
                self.after(0, self.update_stats)
                
                time.sleep(0.01)
        
        except Exception as e:
            print(f"Camera error: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"Error kamera:\n{str(e)}"))
        
        finally:
            if cap:
                cap.release()
            self.camera_running = False
            self.after(0, lambda: self.detection_tab.set_camera_running(False))
            gc.collect()
    
    def open_camera(self):
        """Open camera"""
        for retry in range(3):
            if self.camera_source == "ip":
                url = f"http://{self.config.ip_camera}:4747/video"
                cap = cv2.VideoCapture(url)
                time.sleep(2)
            else:
                cap = cv2.VideoCapture(self.local_camera_index)
                time.sleep(1)
            
            if cap.isOpened() and cap.read()[0]:
                return cap
            
            cap.release()
            if retry < 2:
                time.sleep(1)
        
        self.after(0, lambda: messagebox.showerror("Error", "Gagal membuka kamera!"))
        return None
    
    def stop_camera_feed(self):
        """Stop camera"""
        if not self.camera_running:
            return
        self.stop_camera = True
        messagebox.showinfo("Info", "Kamera sedang dihentikan...")
    
    def calculate_fps(self):
        """Calculate FPS"""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        self.frame_times.append(frame_time)
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        
        if self.frame_times:
            avg = sum(self.frame_times) / len(self.frame_times)
            self.fps = 1.0 / avg if avg > 0 else 0
    
    def log_camera_detection(self, info):
        """Log camera detection"""
        log_entry = {
            "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sumber": "Kamera (Tracking)",
            "object_id": f"ID-{info['object_id']}",
            "kelas_terdeteksi": ", ".join(info['labels']),
            "keputusan": info['keputusan'],
            "confidence": f"{info['confidence']:.2f}",
            "inference_time_ms": f"{self.detection_processor.inference_time:.1f}",
            "fps": f"{self.fps:.1f}",
            "serial_sent": "Yes" if self.serial_manager.connected else "No"
        }
        self.log_manager.add_entry(log_entry)
        self.log_manager.save_append([log_entry])
        
        self.chart_data["timestamps"].append(datetime.now())
        with self.stats_lock:
            self.chart_data["accept"].append(self.accept_count)
            self.chart_data["reject"].append(self.reject_count)
        self.after(0, self.update_live_chart)
    
    # ==================== DISPLAY & STATS ====================
    
    def display_image(self, img_array):
        """Display image"""
        try:
            h, w = img_array.shape[:2]
            scale = min(900/w, 600/h)
            new_w, new_h = max(1, int(w*scale)), max(1, int(h*scale))
            img_resized = cv2.resize(img_array, (new_w, new_h))
            img_pil = Image.fromarray(img_resized)
            img_tk = ImageTk.PhotoImage(img_pil)
            self.after(0, lambda: self.detection_tab.update_image(img_tk))
        except Exception as e:
            print(f"Error displaying image: {e}")
    
    def update_counts(self, keputusan):
        """Update statistics counts"""
        with self.stats_lock:
            if keputusan == "REJECT":
                self.reject_count += 1
            else:
                self.accept_count += 1
    
    def update_stats(self):
        """Update statistics display"""
        with self.stats_lock:
            accept, reject, fps = self.accept_count, self.reject_count, self.fps
        
        tracked = len(self.tracker.objects)
        self.top_bar.update_stats(accept, reject, fps, tracked)
    
    def update_live_chart(self):
        """Update live chart"""
        if not self.chart_data["timestamps"]:
            return
        
        if len(self.chart_data["timestamps"]) > self.max_chart_points:
            for key in ["timestamps", "accept", "reject"]:
                self.chart_data[key] = self.chart_data[key][-self.max_chart_points:]
        
        x_data = list(range(len(self.chart_data["timestamps"])))
        self.chart_tab.update_chart(x_data, self.chart_data["accept"], self.chart_data["reject"])
    
    # ==================== LOG MANAGEMENT ====================
    
    def refresh_log(self):
        """Refresh log display"""
        if not self.log_manager.log_deteksi:
            self.log_tab.update_log("Belum ada log deteksi.\n")
            return
        df = pd.DataFrame(self.log_manager.log_deteksi)
        self.log_tab.update_log(df.to_string(index=False))
    
    def export_log(self):
        """Export log to CSV"""
        if not self.log_manager.log_deteksi:
            messagebox.showinfo("Info", "Tidak ada log untuk diekspor.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            try:
                df = pd.DataFrame(self.log_manager.log_deteksi)
                df.to_csv(file_path, index=False)
                
                total = len(df)
                accepts = sum(1 for log in self.log_manager.log_deteksi if log.get("keputusan") == "ACCEPT")
                rejects = total - accepts
                
                messagebox.showinfo("Success",
                    f"✅ Log exported!\n\nTotal: {total}\n"
                    f"Accept: {accepts} ({accepts/total*100:.1f}%)\n"
                    f"Reject: {rejects} ({rejects/total*100:.1f}%)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export:\n{str(e)}")
    
    def clear_logs(self):
        """Clear all logs"""
        if not messagebox.askyesno("Confirm",
            "Yakin ingin menghapus semua log?\n\nData tidak dapat dikembalikan!"):
            return
        
        self.log_manager.reset()
        self.refresh_log()
        messagebox.showinfo("Success", "✅ Log berhasil dihapus!")
    
    def reset_data(self):
        """Reset all data"""
        if not messagebox.askyesno("Confirm",
            "Yakin ingin mereset semua data?"):
            return
        
        with self.stats_lock:
            self.reject_count = 0
            self.accept_count = 0
        
        self.log_manager.reset()
        self.fps = 0
        self.frame_times = []
        self.chart_data = {"timestamps": [], "accept": [], "reject": []}
        self.detection_processor.processed_objects = {}
        
        self.update_live_chart()
        self.update_stats()
        self.refresh_log()
        self.detection_tab.clear_decision()
        self.detection_tab.clear_image()
        
        gc.collect()
        messagebox.showinfo("Success", "✅ Data berhasil direset!")


if __name__ == "__main__":
    app = EggSorterApp()
    app.mainloop()