"""
Settings Tabs UI - Detection Zone & Model Settings
"""
import customtkinter as ctk
from Core.constants import EMOJI
from UI.ui_components import SettingSlider, InfoPanel


class DetectionSettingsTab:
    """Detection zone settings tab"""
    
    def __init__(self, parent, config, callbacks):
        """
        Args:
            parent: Parent tabview
            config: Config object
            callbacks: Dict of callback functions
        """
        self.parent = parent
        self.config = config
        self.callbacks = callbacks
        self.tab = parent.add(f"{EMOJI['target']} Detection Zone")
        self.setup()
    
    def setup(self):
        """Setup detection settings tab"""
        self.tab.grid_columnconfigure((0,1), weight=1)
        
        # Left - Settings
        left_frame = ctk.CTkFrame(self.tab)
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(
            left_frame, 
            text="Pengaturan Zona Deteksi",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Confidence slider
        self.conf_slider = SettingSlider(
            left_frame,
            title="Minimum Confidence:",
            from_=0.0,
            to=1.0,
            initial_value=self.config.min_conf,
            command=self.callbacks.get('update_conf'),
            unit=""
        )
        self.conf_slider.pack(pady=10, padx=20, fill="x")
        
        # Zone X slider
        self.zone_x_slider = SettingSlider(
            left_frame,
            title="Detection Zone X (pixel):",
            from_=100,
            to=540,
            initial_value=self.config.detection_zone_x,
            command=self.callbacks.get('update_zone_x'),
            unit=" px"
        )
        self.zone_x_slider.pack(pady=10, padx=20, fill="x")
        
        # Tolerance slider
        self.tolerance_slider = SettingSlider(
            left_frame,
            title="Zone Tolerance (±pixel):",
            from_=10,
            to=100,
            initial_value=self.config.detection_zone_tolerance,
            command=self.callbacks.get('update_tolerance'),
            unit=" px"
        )
        self.tolerance_slider.pack(pady=10, padx=20, fill="x")
        
        # Cooldown slider
        self.cooldown_slider = SettingSlider(
            left_frame,
            title="Decision Cooldown (detik):",
            from_=0.5,
            to=5.0,
            initial_value=self.config.decision_cooldown,
            command=self.callbacks.get('update_cooldown'),
            unit=" s"
        )
        self.cooldown_slider.pack(pady=10, padx=20, fill="x")
        
        # Right - Info
        info_text = """
🎯 Detection Zone X:
   Posisi garis vertikal zona deteksi
   • Default: 320px (tengah frame 640px)
   • Sesuaikan dengan posisi conveyor
   
🔍 Zone Tolerance:
   Lebar zona deteksi (kiri-kanan dari garis)
   • Semakin besar = zona lebih lebar
   • Recommended: 40-60px
   
⏱️ Decision Cooldown:
   Jeda waktu minimum antar keputusan
   • Mencegah deteksi ganda
   • Sesuaikan dengan kecepatan conveyor
   • Recommended: 1.5-2.5 detik
   
🧠 Minimum Confidence:
   Threshold keyakinan model
   • Lebih tinggi = lebih yakin tapi kurang sensitif
   • Lebih rendah = lebih sensitif tapi banyak false positive
   • Recommended: 0.25-0.40
        """
        
        right_frame = InfoPanel(self.tab, "Penjelasan Parameter", info_text)
        right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")


class ModelSettingsTab:
    """Model and device settings tab"""
    
    def __init__(self, parent, config, model_manager, callbacks):
        """
        Args:
            parent: Parent tabview
            config: Config object
            model_manager: ModelManager object
            callbacks: Dict of callback functions
        """
        self.parent = parent
        self.config = config
        self.model_manager = model_manager
        self.callbacks = callbacks
        self.tab = parent.add(f"{EMOJI['brain']} Model")
        self.setup()
    
    def setup(self):
        """Setup model settings tab"""
        self.tab.grid_columnconfigure((0,1), weight=1)
        
        # Left - Device & Settings
        left_frame = ctk.CTkFrame(self.tab)
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(
            left_frame, 
            text="Device Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Device selection
        device_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        device_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            device_frame, 
            text="Processing Device:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(15, 10))
        
        device_options = ["cpu"]
        if self.model_manager.cuda_available:
            device_options.append("cuda")
        
        self.device_var = ctk.StringVar(value=self.config.device)
        ctk.CTkSegmentedButton(
            device_frame, 
            values=device_options,
            variable=self.device_var, 
            command=self.callbacks.get('change_device'),
            height=50
        ).pack(pady=10, padx=20, fill="x")
        
        # Device info
        device_info = "CPU Mode"
        if self.model_manager.cuda_available:
            import torch
            gpu_name = torch.cuda.get_device_name(0)
            device_info = f"GPU: {gpu_name}"
        
        self.device_info_label = ctk.CTkLabel(
            device_frame, 
            text=f"ℹ️ {device_info}",
            font=ctk.CTkFont(size=12), 
            text_color="gray"
        )
        self.device_info_label.pack(pady=(5, 15))
        
        # Other settings
        settings_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        settings_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            settings_frame, 
            text="Other Settings:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(15, 10))
        
        self.log_checkbox = ctk.CTkCheckBox(
            settings_frame, 
            text="Enable Logging",
            command=self.callbacks.get('toggle_log'),
            font=ctk.CTkFont(size=13)
        )
        if self.config.aktifkan_log:
            self.log_checkbox.select()
        self.log_checkbox.pack(pady=10, padx=20, anchor="w")
        
        self.alert_checkbox = ctk.CTkCheckBox(
            settings_frame, 
            text="Enable Alerts",
            command=self.callbacks.get('toggle_alert'),
            font=ctk.CTkFont(size=13)
        )
        if self.config.alert_enabled:
            self.alert_checkbox.select()
        self.alert_checkbox.pack(pady=10, padx=20, anchor="w")
        
        self.sound_checkbox = ctk.CTkCheckBox(
            settings_frame, 
            text="Enable Sound",
            command=self.callbacks.get('toggle_sound'),
            font=ctk.CTkFont(size=13)
        )
        if self.config.alert_sound_enabled:
            self.sound_checkbox.select()
        self.sound_checkbox.pack(pady=(10, 15), padx=20, anchor="w")
        
        # Save/Load config
        config_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        config_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkButton(
            config_frame, 
            text=f"{EMOJI['save']} Save Config",
            command=self.callbacks.get('save_config'), 
            fg_color="#3498db",
            hover_color="#2980b9", 
            height=45,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        ctk.CTkButton(
            config_frame, 
            text=f"{EMOJI['folder']} Load Config",
            command=self.callbacks.get('load_config'), 
            fg_color="#9b59b6",
            hover_color="#8e44ad", 
            height=45,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", expand=True, fill="x", padx=(10, 0))
        
        # Right - Model Info
        self._setup_model_info(self.tab)
    
    def _setup_model_info(self, parent):
        """Setup model information panel"""
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(
            right_frame, 
            text="Model Information",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        info_frame = ctk.CTkFrame(right_frame, fg_color="#2b2b2b")
        info_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        from pathlib import Path
        model_path = Path("models/best.pt")
        
        model_info = f"""
🧠 Model: YOLOv8
📍 Path: {model_path}
📊 Classes: {len(self.model_manager.model.names)}

Detected Classes:
{chr(10).join([f"  • {i}: {name}" for i, name in self.model_manager.model.names.items()])}

💻 Device Information:
"""
        
        if self.model_manager.cuda_available:
            import torch
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            model_info += f"""
  ✅ CUDA Available
  🎮 GPU: {gpu_name}
  💾 Memory: {gpu_memory:.1f} GB
  
⚡ Performance Mode: HIGH
            """
        else:
            model_info += """
  ⚠️ CUDA Not Available
  💻 Using: CPU Only
  
⚙️ Performance Mode: STANDARD
            """
        
        ctk.CTkLabel(
            info_frame, 
            text=model_info, 
            justify="left",
            font=ctk.CTkFont(size=11)
        ).pack(pady=20, padx=20, anchor="w")
    
    def update_device_info(self, info_text, color="gray"):
        """Update device info label"""
        self.device_info_label.configure(text=info_text, text_color=color)