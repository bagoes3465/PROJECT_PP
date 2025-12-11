"""
Detection Tab UI
"""
import customtkinter as ctk
from Core.constants import EMOJI


class DetectionTab:
    """Detection tab UI"""
    
    def __init__(self, parent, callbacks):
        """
        Args:
            parent: Parent tabview
            callbacks: Dict of callback functions
                - upload_image
                - start_camera
                - stop_camera
                - reset_data
        """
        self.parent = parent
        self.callbacks = callbacks
        self.tab = parent.add(f"{EMOJI['camera']} Detection")
        self.setup()
    
    def setup(self):
        """Setup detection tab"""
        self.tab.grid_columnconfigure(0, weight=1)
        self.tab.grid_rowconfigure(1, weight=1)
        
        # Control buttons
        control_frame = ctk.CTkFrame(self.tab, height=80)
        control_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        control_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        ctk.CTkButton(
            control_frame, 
            text=f"{EMOJI['upload']} Upload Gambar",
            command=self.callbacks['upload_image'], 
            height=50, 
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.start_btn = ctk.CTkButton(
            control_frame, 
            text=f"{EMOJI['play']} Mulai Kamera",
            command=self.callbacks['start_camera'], 
            fg_color="#27ae60", 
            hover_color="#229954", 
            height=50, 
            font=ctk.CTkFont(size=14)
        )
        self.start_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            control_frame, 
            text=f"{EMOJI['stop']} Stop Kamera",
            command=self.callbacks['stop_camera'], 
            fg_color="#e74c3c", 
            hover_color="#c0392b", 
            height=50, 
            state="disabled",
            font=ctk.CTkFont(size=14)
        )
        self.stop_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(
            control_frame, 
            text=f"{EMOJI['refresh']} Reset Data",
            command=self.callbacks['reset_data'], 
            fg_color="#8e44ad", 
            hover_color="#7d3c98",
            height=50, 
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        # Image display
        image_frame = ctk.CTkFrame(self.tab)
        image_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        image_frame.grid_rowconfigure(0, weight=1)
        image_frame.grid_columnconfigure(0, weight=1)
        
        self.image_label = ctk.CTkLabel(
            image_frame, 
            text="Tidak ada gambar",
            font=ctk.CTkFont(size=16)
        )
        self.image_label.grid(row=0, column=0, sticky="nsew")
        
        # Decision label
        self.decision_label = ctk.CTkLabel(
            self.tab, 
            text="", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.decision_label.grid(row=2, column=0, padx=20, pady=10)
        
        # Info
        info_frame = ctk.CTkFrame(self.tab, fg_color="#2b2b2b", corner_radius=8)
        info_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        ctk.CTkLabel(
            info_frame, 
            text="ℹ️ Conveyor Mode: Telur dihitung 1x saat melewati Detection Zone",
            font=ctk.CTkFont(size=12), 
            text_color="gray"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            info_frame, 
            text="📋 Kelas: ✅ ACCEPT (clean, yellow egg) | ❌ REJECT (crack, dirty)",
            font=ctk.CTkFont(size=11), 
            text_color="gray"
        ).pack(pady=(0, 10))
    
    def set_camera_running(self, running):
        """Update button states based on camera status"""
        if running:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
    
    def update_image(self, img_tk):
        """Update displayed image"""
        self.image_label.configure(image=img_tk, text="")
        self.image_label.image = img_tk
    
    def update_decision(self, decision):
        """Update decision label"""
        color = "#2ecc71" if decision == "ACCEPT" else "#e74c3c"
        self.decision_label.configure(
            text=f"{EMOJI['brain']} Keputusan: {decision}", 
            text_color=color
        )
    
    def clear_image(self):
        """Clear image display"""
        if hasattr(self.image_label, 'image'):
            try:
                del self.image_label.image
            except:
                pass
        self.image_label.configure(image=None, text="Tidak ada gambar")
    
    def clear_decision(self):
        """Clear decision label"""
        self.decision_label.configure(text="")