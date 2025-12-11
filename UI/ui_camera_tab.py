"""
Camera Settings Tab UI
"""
import customtkinter as ctk
from Core.constants import EMOJI


class CameraTab:
    """Camera settings tab"""
    
    def __init__(self, parent, callbacks, initial_ip="192.168.1.6"):
        """
        Args:
            parent: Parent tabview
            callbacks: Dict of callback functions
                - change_source
                - refresh_cameras
            initial_ip: Initial IP camera address
        """
        self.parent = parent
        self.callbacks = callbacks
        self.initial_ip = initial_ip
        self.tab = parent.add(f"{EMOJI['camera']} Camera")
        self.setup()
    
    def setup(self):
        """Setup camera tab"""
        self.tab.grid_columnconfigure((0,1), weight=1)
        
        # Left column - Camera Source
        left_frame = ctk.CTkFrame(self.tab)
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(
            left_frame, 
            text="Sumber Kamera", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        self.source_var = ctk.StringVar(value="Webcam")
        source_menu = ctk.CTkSegmentedButton(
            left_frame, 
            values=["Webcam", "DroidCam IP"],
            variable=self.source_var, 
            command=self._on_source_change, 
            height=40
        )
        source_menu.pack(pady=10, padx=20, fill="x")
        source_menu.set("Webcam")
        
        # Webcam selection
        self.local_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        self.local_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            self.local_frame, 
            text="Pilih Kamera Lokal:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 10))
        
        cam_frame = ctk.CTkFrame(self.local_frame, fg_color="transparent")
        cam_frame.pack(fill="x")
        
        self.camera_var = ctk.StringVar(value="Detecting...")
        self.camera_menu = ctk.CTkOptionMenu(
            cam_frame, 
            values=["Detecting..."],
            variable=self.camera_var, 
            height=40
        )
        self.camera_menu.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.detect_btn = ctk.CTkButton(
            cam_frame, 
            text=f"{EMOJI['search']}", 
            width=50, 
            height=40, 
            command=self.callbacks['refresh_cameras']
        )
        self.detect_btn.pack(side="left")
        
        # IP Camera
        self.ip_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        self.ip_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            self.ip_frame, 
            text="IP Address DroidCam:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 10))
        
        self.ip_entry = ctk.CTkEntry(
            self.ip_frame, 
            placeholder_text="192.168.1.6", 
            height=40, 
            font=ctk.CTkFont(size=14)
        )
        self.ip_entry.insert(0, self.initial_ip)
        self.ip_entry.pack(fill="x")
        
        self.ip_frame.pack_forget()
        
        # Right column - Info
        right_frame = ctk.CTkFrame(self.tab)
        right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(
            right_frame, 
            text="Informasi Kamera",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        info_text = """
📹 Webcam: Gunakan kamera lokal (USB/Built-in)
        
📱 DroidCam IP: Gunakan smartphone sebagai kamera
   • Install app DroidCam di Android/iOS
   • Masukkan IP address yang ditampilkan di app
   • Pastikan device dalam jaringan yang sama
   
💡 Tips:
   • Posisikan kamera tegak lurus conveyor
   • Pastikan pencahayaan cukup
   • Jarak ideal: 30-50cm dari telur
   • Hindari backlight
        """
        
        ctk.CTkLabel(
            right_frame, 
            text=info_text, 
            justify="left",
            font=ctk.CTkFont(size=12)
        ).pack(pady=20, padx=20, anchor="w")
    
    def _on_source_change(self, value):
        """Handle camera source change"""
        if value == "Webcam":
            self.local_frame.pack(pady=20, padx=20, fill="x")
            self.ip_frame.pack_forget()
            source = "local"
        else:
            self.local_frame.pack_forget()
            self.ip_frame.pack(pady=20, padx=20, fill="x")
            source = "ip"
        
        if self.callbacks['change_source']:
            self.callbacks['change_source'](source)
    
    def update_camera_list(self, camera_names):
        """Update available camera list"""
        if not camera_names:
            camera_names = ["No Camera Detected"]
        self.camera_menu.configure(values=camera_names)
        if camera_names:
            self.camera_var.set(camera_names[0])
    
    def get_selected_camera(self):
        """Get selected camera name"""
        return self.camera_var.get()
    
    def get_ip_address(self):
        """Get IP camera address"""
        return self.ip_entry.get()
    
    def set_detect_button_state(self, state, text=None):
        """Set detect button state"""
        self.detect_btn.configure(state=state)
        if text:
            self.detect_btn.configure(text=text)