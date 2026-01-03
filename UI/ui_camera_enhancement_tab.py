"""
Camera Enhancement Settings Tab
"""
import customtkinter as ctk
from Core.constants import EMOJI
from UI.ui_components import SettingSlider


class CameraEnhancementTab:
    """Camera image enhancement settings"""
    
    def __init__(self, parent, processor, callbacks):
        """
        Args:
            parent: Parent tabview
            processor: CameraProcessor instance
            callbacks: Dict of callback functions
        """
        self.parent = parent
        self.processor = processor
        self.callbacks = callbacks
        self.tab = parent.add(f"{EMOJI['lightning']} Enhancement")
        self.setup()
    
    def setup(self):
        """Setup enhancement tab"""
        self.tab.grid_columnconfigure((0, 1), weight=1)
        self.tab.grid_rowconfigure(0, weight=1)
        
        # Left column - Basic Settings
        left_frame = ctk.CTkScrollableFrame(self.tab)
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(
            left_frame,
            text="Basic Image Enhancement",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Enable/Disable Toggle
        toggle_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b", corner_radius=8)
        toggle_frame.pack(pady=10, padx=20, fill="x")
        
        self.enable_switch = ctk.CTkSwitch(
            toggle_frame,
            text="Enable Image Processing",
            command=self.toggle_processing,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.enable_switch.pack(pady=15, padx=20)
        if self.processor.enable_processing:
            self.enable_switch.select()
        
        # Basic sliders
        self.brightness_slider = SettingSlider(
            left_frame,
            title="Brightness:",
            from_=-50,
            to=50,
            initial_value=self.processor.brightness,
            command=self.update_brightness,
            unit=""
        )
        self.brightness_slider.pack(pady=10, padx=20, fill="x")
        
        self.contrast_slider = SettingSlider(
            left_frame,
            title="Contrast:",
            from_=0.5,
            to=3.0,
            initial_value=self.processor.contrast,
            command=self.update_contrast,
            unit="x"
        )
        self.contrast_slider.pack(pady=10, padx=20, fill="x")
        
        self.sharpness_slider = SettingSlider(
            left_frame,
            title="Sharpness:",
            from_=0.0,
            to=2.0,
            initial_value=self.processor.sharpness,
            command=self.update_sharpness,
            unit=""
        )
        self.sharpness_slider.pack(pady=10, padx=20, fill="x")
        
        self.gamma_slider = SettingSlider(
            left_frame,
            title="Gamma Correction:",
            from_=0.5,
            to=2.0,
            initial_value=self.processor.gamma,
            command=self.update_gamma,
            unit=""
        )
        self.gamma_slider.pack(pady=10, padx=20, fill="x")
        
        # Resolution selector
        res_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        res_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            res_frame,
            text="Processing Resolution:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        current_res = f"{self.processor.target_resolution[0]}x{self.processor.target_resolution[1]}"
        self.resolution_var = ctk.StringVar(value=current_res)
        
        ctk.CTkSegmentedButton(
            res_frame,
            values=["320x240", "416x312", "640x480"],
            variable=self.resolution_var,
            command=self.update_resolution,
            height=40
        ).pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            res_frame,
            text="⚡ Lower = Faster | 🎯 Higher = Better Quality",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=(0, 15))
        
        # Preset buttons
        preset_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        preset_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            preset_frame,
            text="Quick Presets:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(0, 10))
        
        preset_btns = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_btns.pack(fill="x")
        
        ctk.CTkButton(
            preset_btns,
            text="🌙 Low Light",
            command=self.preset_low_light,
            fg_color="#8e44ad",
            height=40
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        ctk.CTkButton(
            preset_btns,
            text="☀️ Bright",
            command=self.preset_bright,
            fg_color="#f39c12",
            height=40
        ).pack(side="left", expand=True, fill="x", padx=5)
        
        ctk.CTkButton(
            preset_btns,
            text="🎯 Optimal",
            command=self.preset_optimal,
            fg_color="#27ae60",
            height=40
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        ctk.CTkButton(
            left_frame,
            text=f"{EMOJI['refresh']} Reset to Default",
            command=self.reset_settings,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=45,
            font=ctk.CTkFont(size=13)
        ).pack(pady=10, padx=20, fill="x")
        
        # Right column - Advanced Settings
        right_frame = ctk.CTkFrame(self.tab)
        right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(
            right_frame,
            text="Advanced Enhancement",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Advanced options
        advanced_frame = ctk.CTkFrame(right_frame, fg_color="#2b2b2b")
        advanced_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            advanced_frame,
            text="Advanced Filters:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10), anchor="w", padx=20)
        
        # CLAHE
        self.clahe_check = ctk.CTkCheckBox(
            advanced_frame,
            text="Enable CLAHE (Adaptive Contrast)",
            command=self.toggle_clahe,
            font=ctk.CTkFont(size=13)
        )
        if self.processor.enable_clahe:
            self.clahe_check.select()
        self.clahe_check.pack(pady=5, padx=20, anchor="w")
        
        ctk.CTkLabel(
            advanced_frame,
            text="   → Meningkatkan kontras area gelap/terang",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(pady=(0, 10), padx=20, anchor="w")
        
        # Denoise
        self.denoise_check = ctk.CTkCheckBox(
            advanced_frame,
            text="Enable Denoising (Noise Reduction)",
            command=self.toggle_denoise,
            font=ctk.CTkFont(size=13)
        )
        if self.processor.enable_denoise:
            self.denoise_check.select()
        self.denoise_check.pack(pady=5, padx=20, anchor="w")
        
        ctk.CTkLabel(
            advanced_frame,
            text="   → Mengurangi noise kamera (LAMBAT!)",
            font=ctk.CTkFont(size=10),
            text_color="#e74c3c"
        ).pack(pady=(0, 10), padx=20, anchor="w")
        
        # White Balance
        self.wb_check = ctk.CTkCheckBox(
            advanced_frame,
            text="Enable Auto White Balance",
            command=self.toggle_white_balance,
            font=ctk.CTkFont(size=13)
        )
        if self.processor.enable_white_balance:
            self.wb_check.select()
        self.wb_check.pack(pady=5, padx=20, anchor="w")
        
        ctk.CTkLabel(
            advanced_frame,
            text="   → Normalisasi warna untuk berbagai cahaya",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(pady=(0, 15), padx=20, anchor="w")
        
        # Info panel
        info_frame = ctk.CTkFrame(right_frame, fg_color="#1a1a1a", corner_radius=8)
        info_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            info_frame,
            text="💡 Tips Penggunaan",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        tips_text = """
📌 Basic Settings (RINGAN):
   • Brightness: Atur sesuai pencahayaan ruangan
   • Contrast: 1.2-1.5 untuk hasil lebih tajam
   • Sharpness: 0.5-1.0 untuk deteksi crack
   • Gamma: 0.8-1.2 untuk normalisasi cahaya

⚡ Performance:
   • Resolution 320x240 → FPS tinggi
   • Resolution 640x480 → Akurasi tinggi
   • Resolution 416x312 → BALANCED (recommended)

🎯 Advanced Filters:
   • CLAHE: Bagus untuk cahaya tidak merata
   • Denoise: Hanya jika kamera sangat noisy
   • White Balance: Aktifkan jika warna tidak konsisten

⚠️ Warning:
   • Denoise SANGAT LAMBAT (-50% FPS)
   • Gunakan hanya jika sangat diperlukan
   • Test di kamera real-time dulu

✨ Recommended Settings:
   Brightness: +10
   Contrast: 1.2
   Sharpness: 0.5
   Gamma: 1.0
   CLAHE: ON
   Denoise: OFF
   White Balance: ON
   Resolution: 416x312
        """
        
        ctk.CTkLabel(
            info_frame,
            text=tips_text,
            justify="left",
            font=ctk.CTkFont(size=11)
        ).pack(pady=10, padx=20, anchor="w")
    
    # Callbacks
    def toggle_processing(self):
        enabled = self.enable_switch.get()
        self.processor.toggle_processing(enabled)
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()
    
    def update_brightness(self, value):
        self.processor.set_brightness(value)
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()
    
    def update_contrast(self, value):
        self.processor.set_contrast(value)
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()
    
    def update_sharpness(self, value):
        self.processor.set_sharpness(value)
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()
    
    def update_gamma(self, value):
        self.processor.set_gamma(value)
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()
    
    def update_resolution(self, value):
        w, h = map(int, value.split('x'))
        self.processor.set_resolution(w, h)
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()
    
    def toggle_clahe(self):
        self.processor.toggle_clahe(self.clahe_check.get())
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()
    
    def toggle_denoise(self):
        enabled = self.denoise_check.get()
        self.processor.toggle_denoise(enabled)
        if enabled:
            from tkinter import messagebox
            messagebox.showwarning(
                "Performance Warning",
                "⚠️ Denoising akan menurunkan FPS hingga 50%!\n\n"
                "Gunakan hanya jika kamera sangat noisy."
            )
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()
    
    def toggle_white_balance(self):
        self.processor.toggle_white_balance(self.wb_check.get())
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()
    
    def reset_settings(self):
        from tkinter import messagebox
        if messagebox.askyesno("Reset Settings", "Reset semua settings ke default?"):
            self.processor.reset_to_default()
            
            # Update UI
            self.brightness_slider.set(0)
            self.contrast_slider.set(1.0)
            self.sharpness_slider.set(0.0)
            self.gamma_slider.set(1.0)
            self.resolution_var.set("640x480")
            
            if self.processor.enable_processing:
                self.enable_switch.select()
            else:
                self.enable_switch.deselect()
            
            self.clahe_check.deselect()
            self.denoise_check.deselect()
            self.wb_check.deselect()
            
            if self.callbacks.get('on_settings_change'):
                self.callbacks['on_settings_change']()
            
            messagebox.showinfo("Success", "✅ Settings reset to default!")
    
    # Presets
    def preset_low_light(self):
        """Preset for low light conditions"""
        self.processor.set_brightness(20)
        self.processor.set_contrast(1.3)
        self.processor.set_sharpness(0.5)
        self.processor.set_gamma(1.2)
        self.processor.toggle_clahe(True)
        self.processor.toggle_white_balance(True)
        
        self.update_ui_from_processor()
        
        from tkinter import messagebox
        messagebox.showinfo("Preset Applied", "🌙 Low Light preset diterapkan!")
    
    def preset_bright(self):
        """Preset for bright conditions"""
        self.processor.set_brightness(-10)
        self.processor.set_contrast(1.0)
        self.processor.set_sharpness(0.3)
        self.processor.set_gamma(0.9)
        self.processor.toggle_clahe(False)
        self.processor.toggle_white_balance(True)
        
        self.update_ui_from_processor()
        
        from tkinter import messagebox
        messagebox.showinfo("Preset Applied", "☀️ Bright preset diterapkan!")
    
    def preset_optimal(self):
        """Optimal preset for egg detection"""
        self.processor.set_brightness(10)
        self.processor.set_contrast(1.2)
        self.processor.set_sharpness(0.5)
        self.processor.set_gamma(1.0)
        self.processor.toggle_clahe(True)
        self.processor.toggle_denoise(False)
        self.processor.toggle_white_balance(True)
        self.processor.set_resolution(416, 312)
        
        self.update_ui_from_processor()
        
        from tkinter import messagebox
        messagebox.showinfo("Preset Applied", 
            "🎯 Optimal preset diterapkan!\n\n"
            "Recommended untuk deteksi telur:\n"
            "• Balance antara speed & accuracy\n"
            "• CLAHE untuk kontras adaptif\n"
            "• White Balance untuk normalisasi warna")
    
    def update_ui_from_processor(self):
        """Update UI from processor settings"""
        self.brightness_slider.set(self.processor.brightness)
        self.contrast_slider.set(self.processor.contrast)
        self.sharpness_slider.set(self.processor.sharpness)
        self.gamma_slider.set(self.processor.gamma)
        
        res = f"{self.processor.target_resolution[0]}x{self.processor.target_resolution[1]}"
        self.resolution_var.set(res)
        
        if self.processor.enable_clahe:
            self.clahe_check.select()
        else:
            self.clahe_check.deselect()
        
        if self.processor.enable_denoise:
            self.denoise_check.select()
        else:
            self.denoise_check.deselect()
        
        if self.processor.enable_white_balance:
            self.wb_check.select()
        else:
            self.wb_check.deselect()
        
        if self.callbacks.get('on_settings_change'):
            self.callbacks['on_settings_change']()