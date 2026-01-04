"""
Settings Tabs UI - Detection Zone & Model Settings
Enhanced with Model Selection Feature
"""
import customtkinter as ctk
from Core.constants import EMOJI
from UI.ui_components import SettingSlider, InfoPanel
from tkinter import filedialog, messagebox
from pathlib import Path
import os


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
        self.current_model_path = Path(r"Data Folder\models\best.pt")
        self.setup()
    
    def setup(self):
        """Setup model settings tab"""
        self.tab.grid_columnconfigure((0,1), weight=1)
        self.tab.grid_rowconfigure(0, weight=1)
        
        # Left - Device & Settings (WITH SCROLLABLE FRAME)
        left_scroll = ctk.CTkScrollableFrame(self.tab)
        left_scroll.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        left_frame = ctk.CTkFrame(left_scroll, fg_color="transparent")
        left_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            left_frame, 
            text="Model & Device Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # === MODEL SELECTION SECTION (NEW) ===
        model_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b", corner_radius=10)
        model_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            model_frame, 
            text="Model Selection:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5), padx=20, anchor="w")
        
        # Current model display
        model_display_frame = ctk.CTkFrame(model_frame, fg_color="#1a1a1a", corner_radius=8)
        model_display_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            model_display_frame,
            text="Current Model:",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(10, 5), padx=15, anchor="w")
        
        self.model_path_label = ctk.CTkLabel(
            model_display_frame,
            text=str(self.current_model_path),
            font=ctk.CTkFont(size=11),
            text_color="#3498db",
            wraplength=450,
            justify="left"
        )
        self.model_path_label.pack(pady=(0, 10), padx=15, anchor="w")
        
        # Browse button
        browse_btn_frame = ctk.CTkFrame(model_frame, fg_color="transparent")
        browse_btn_frame.pack(pady=10, padx=20, fill="x")
        
        self.browse_model_btn = ctk.CTkButton(
            browse_btn_frame,
            text="📂 Browse Model...",
            command=self.browse_model,
            fg_color="#8e44ad",
            hover_color="#7d3c98",
            height=45,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.browse_model_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.reload_model_btn = ctk.CTkButton(
            browse_btn_frame,
            text="🔄 Reload Model",
            command=self.reload_model,
            fg_color="#e67e22",
            hover_color="#d35400",
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled"
        )
        self.reload_model_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        # Model info
        model_info_frame = ctk.CTkFrame(model_frame, fg_color="transparent")
        model_info_frame.pack(pady=5, padx=20, fill="x")
        
        self.model_info_label = ctk.CTkLabel(
            model_info_frame,
            text="ℹ️ Select a .pt model file to load",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        )
        self.model_info_label.pack(pady=(0, 15), anchor="w")
        
        # Separator
        separator1 = ctk.CTkFrame(left_frame, height=2, fg_color="gray30")
        separator1.pack(pady=15, padx=20, fill="x")
        
        # Device selection
        device_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        device_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            device_frame, 
            text="Processing Device:",
            font=ctk.CTkFont(size=14, weight="bold")
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
            font=ctk.CTkFont(size=14, weight="bold")
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
    
    def browse_model(self):
        """Browse and select model file"""
        file_path = filedialog.askopenfilename(
            title="Select YOLO Model File",
            initialdir=str(Path("Data Folder/models")),
            filetypes=[
                ("PyTorch Model", "*.pt"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        model_path = Path(file_path)
        
        # Validate file exists
        if not model_path.exists():
            messagebox.showerror("Error", f"File tidak ditemukan:\n{model_path}")
            return
        
        # Validate file extension
        if model_path.suffix.lower() != '.pt':
            if not messagebox.askyesno("Warning", 
                f"File yang dipilih bukan file .pt\n\n"
                f"File: {model_path.name}\n\n"
                f"Lanjutkan?"):
                return
        
        # Update UI
        self.current_model_path = model_path
        self.model_path_label.configure(text=str(model_path))
        self.model_info_label.configure(
            text=f"📦 Model selected: {model_path.name}\n"
                 f"   Size: {model_path.stat().st_size / 1024 / 1024:.2f} MB",
            text_color="#3498db"
        )
        self.reload_model_btn.configure(state="normal")
        
        # Ask to load immediately
        if messagebox.askyesno("Load Model",
            f"Model baru dipilih:\n{model_path.name}\n\n"
            f"Load model sekarang?\n\n"
            f"⚠️ Warning: Kamera akan dihentikan jika sedang berjalan"):
            self.reload_model()
    
    def reload_model(self):
        """Reload model from selected path"""
        try:
            # Check if camera is running
            if hasattr(self.callbacks.get('check_camera_running'), '__call__'):
                if self.callbacks['check_camera_running']():
                    messagebox.showwarning("Warning",
                        "Kamera sedang berjalan!\n\n"
                        "Stop kamera terlebih dahulu sebelum reload model.")
                    return
            
            # Confirm reload
            if not messagebox.askyesno("Confirm Reload",
                f"Reload model dari:\n{self.current_model_path.name}\n\n"
                f"Proses ini akan memakan waktu beberapa detik.\n"
                f"Lanjutkan?"):
                return
            
            # Disable buttons during load
            self.browse_model_btn.configure(state="disabled")
            self.reload_model_btn.configure(state="disabled")
            self.model_info_label.configure(
                text="⏳ Loading model...",
                text_color="#f39c12"
            )
            
            # Force update UI
            self.tab.update()
            
            # Load model
            from ultralytics import YOLO
            import torch
            
            # Clear cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            print(f"Loading model from: {self.current_model_path}")
            new_model = YOLO(str(self.current_model_path))
            
            # Validate model
            if not hasattr(new_model, 'names') or not new_model.names:
                raise ValueError("Invalid model: No class names found")
            
            # Replace old model
            self.model_manager.model = new_model
            
            # Update info
            self.model_info_label.configure(
                text=f"✅ Model loaded successfully!\n"
                     f"   Classes: {len(new_model.names)} | Device: {self.config.device}",
                text_color="#2ecc71"
            )
            
            # Update model info panel
            self._update_model_info_panel()
            
            messagebox.showinfo("Success",
                f"✅ Model berhasil dimuat!\n\n"
                f"Path: {self.current_model_path.name}\n"
                f"Classes: {len(new_model.names)}\n"
                f"Device: {self.config.device}")
            
        except Exception as e:
            self.model_info_label.configure(
                text=f"❌ Failed to load model!\n   Error: {str(e)[:50]}...",
                text_color="#e74c3c"
            )
            messagebox.showerror("Error",
                f"Gagal memuat model!\n\n"
                f"Error: {str(e)}\n\n"
                f"Pastikan file model valid (.pt) dan kompatibel dengan YOLO.")
        
        finally:
            # Re-enable buttons
            self.browse_model_btn.configure(state="normal")
            self.reload_model_btn.configure(state="normal")
    
    def _setup_model_info(self, parent):
        """Setup model information panel"""
        # Right panel with scrollable frame
        right_scroll = ctk.CTkScrollableFrame(parent)
        right_scroll.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        right_frame = ctk.CTkFrame(right_scroll, fg_color="transparent")
        right_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            right_frame, 
            text="Model Information",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        self.info_textbox = ctk.CTkTextbox(
            right_frame,
            font=ctk.CTkFont(size=12),
            wrap="word",
            height=600  # Set minimum height for better scrolling
        )
        self.info_textbox.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Initial info
        self._update_model_info_panel()
    
    def _update_model_info_panel(self):
        """Update model info textbox"""
        model_info = f"""🧠 Model Information
{'='*50}

📦 Current Model:
   {self.current_model_path}

📊 Classes Detected: {len(self.model_manager.model.names)}

Detected Classes:
"""
        
        for i, name in self.model_manager.model.names.items():
            model_info += f"  • {i}: {name}\n"
        
        model_info += f"\n{'='*50}\n💻 Device Information:\n"
        
        if self.model_manager.cuda_available:
            import torch
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            vram_allocated = torch.cuda.memory_allocated(0) / 1024**3
            model_info += f"""
  ✅ CUDA Available
  🎮 GPU: {gpu_name}
  💾 Total VRAM: {gpu_memory:.2f} GB
  💾 Allocated: {vram_allocated:.2f} GB
  🔧 Current Device: {self.config.device}
  
⚡ Performance Mode: HIGH
"""
        else:
            model_info += """
  ⚠️ CUDA Not Available
  💻 Using: CPU Only
  
⚙️ Performance Mode: STANDARD
"""
        
        model_info += f"""
{'='*50}
📝 How to Use:

1. Click "📂 Browse Model..." to select a new .pt model
2. Model will be validated and info displayed
3. Click "🔄 Reload Model" to load the selected model
4. Model will be hot-swapped without restarting app

⚠️ Important Notes:
• Stop camera before reloading model
• Only YOLO .pt models are supported
• Model must be compatible with current YOLO version
• Larger models need more VRAM/RAM
• Test model with sample images after loading

💡 Tips:
• Keep models in 'Data Folder/models/' directory
• Use YOLOv11n/s for fast inference
• Use YOLOv11m/l for better accuracy
• Custom trained models work perfectly!
"""
        
        self.info_textbox.delete("1.0", "end")
        self.info_textbox.insert("1.0", model_info)
        self.info_textbox.configure(state="disabled")
    
    def update_device_info(self, info_text, color="gray"):
        """Update device info label"""
        self.device_info_label.configure(text=info_text, text_color=color)