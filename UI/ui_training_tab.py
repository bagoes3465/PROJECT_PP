"""
Training Tab UI
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from Core.constants import EMOJI


class TrainingTab:
    """Training tab UI"""
    
    def __init__(self, parent, training_manager, config):
        """
        Args:
            parent: Parent tabview
            training_manager: TrainingManager instance
            config: Config instance
        """
        self.parent = parent
        self.training_manager = training_manager
        self.config = config
        self.tab = parent.add(f"{EMOJI['brain']} Training")
        self.setup()
        
        # Start output monitor
        self.monitor_training_output()
    
    def setup(self):
        """Setup training tab"""
        self.tab.grid_columnconfigure(0, weight=1)
        self.tab.grid_rowconfigure(0, weight=1)
        
        scroll_frame = ctk.CTkScrollableFrame(self.tab)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=1)
        
        # Left Panel - Configuration
        self._setup_config_panel(scroll_frame)
        
        # Right Panel - Output
        self._setup_output_panel(scroll_frame)
        
        # Info Panel
        self._setup_info_panel(scroll_frame)
    
    def _setup_config_panel(self, parent):
        """Setup configuration panel"""
        left_frame = ctk.CTkFrame(parent)
        left_frame.grid(row=0, column=0, rowspan=2, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(left_frame, text="YOLO Training Configuration",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Dataset path
        dataset_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        dataset_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(dataset_frame, text="Dataset Path (data.yaml):",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        path_frame = ctk.CTkFrame(dataset_frame, fg_color="transparent")
        path_frame.pack(pady=10, padx=20, fill="x")
        
        self.dataset_path_var = ctk.StringVar(
            value=r"E:\PROJECT_PP\Data Folder\dataset\datav11\data.yaml"
        )
        self.dataset_entry = ctk.CTkEntry(path_frame, textvariable=self.dataset_path_var,
                                        height=40, font=ctk.CTkFont(size=12))
        self.dataset_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(path_frame, text="📁", width=50, height=40,
                    command=self.browse_dataset).pack(side="left")
        
        # Model selection
        model_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        model_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(model_frame, text="Base Model:",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        self.model_var = ctk.StringVar(value="yolo11n.pt")
        ctk.CTkSegmentedButton(model_frame, 
                            values=["yolo11n.pt", "yolo11s.pt", "yolo11m.pt"],
                            variable=self.model_var, height=40).pack(
                                pady=10, padx=20, fill="x")
        
        # Parameters
        params_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        params_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(params_frame, text="Training Parameters:",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        # Epochs
        self._create_param_entry(params_frame, "Epochs:", "100", "epochs_var")
        
        # Batch
        self._create_param_entry(params_frame, "Batch Size:", "8", "batch_var")
        
        # Image size
        imgsz_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        imgsz_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(imgsz_frame, text="Image Size:", width=100, anchor="w").pack(side="left")
        self.imgsz_var = ctk.StringVar(value="416")
        ctk.CTkSegmentedButton(imgsz_frame, values=["320", "416", "640"],
                            variable=self.imgsz_var, height=35).pack(
                                side="left", padx=10, fill="x", expand=True)
        
        # Workers
        self._create_param_entry(params_frame, "Workers:", "2", "workers_var")
        
        # Patience
        self._create_param_entry(params_frame, "Patience:", "20", "patience_var", pady=(5, 15))
        
        # Advanced options
        advanced_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        advanced_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(advanced_frame, text="Advanced Options:",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        self.cache_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(advanced_frame, text="Enable Cache", 
                    variable=self.cache_var).pack(pady=5, padx=20, anchor="w")
        
        self.amp_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(advanced_frame, text="Enable AMP (Mixed Precision)",
                    variable=self.amp_var).pack(pady=5, padx=20, anchor="w")
        
        self.plots_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(advanced_frame, text="Generate Plots",
                    variable=self.plots_var).pack(pady=(5, 15), padx=20, anchor="w")
        
        # Control buttons
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=20, padx=20, fill="x")
        
        self.start_btn = ctk.CTkButton(
            btn_frame, text="🚀 Start Training",
            command=self.start_training,
            fg_color="#27ae60", hover_color="#229954",
            height=50, font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_btn.pack(fill="x", pady=(0, 10))
        
        self.stop_btn = ctk.CTkButton(
            btn_frame, text="🛑 Stop Training",
            command=self.stop_training,
            fg_color="#e74c3c", hover_color="#c0392b",
            height=50, state="disabled",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.stop_btn.pack(fill="x")
    
    def _setup_output_panel(self, parent):
        """Setup output panel"""
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(right_frame, text="Training Output",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Progress info
        progress_frame = ctk.CTkFrame(right_frame, fg_color="#2b2b2b", height=100)
        progress_frame.pack(pady=10, padx=20, fill="x")
        progress_frame.pack_propagate(False)
        
        info_grid = ctk.CTkFrame(progress_frame, fg_color="transparent")
        info_grid.pack(expand=True, pady=10)
        
        # Status
        status_container = ctk.CTkFrame(info_grid, fg_color="transparent")
        status_container.pack(pady=5)
        ctk.CTkLabel(status_container, text="Status:", 
                    font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        self.status_label = ctk.CTkLabel(
            status_container, text="Ready",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        )
        self.status_label.pack(side="left")
        
        # Epoch progress
        epoch_container = ctk.CTkFrame(info_grid, fg_color="transparent")
        epoch_container.pack(pady=5)
        ctk.CTkLabel(epoch_container, text="Epoch:", 
                    font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        self.epoch_label = ctk.CTkLabel(
            epoch_container, text="0/0",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.epoch_label.pack(side="left")
        
        # Output console
        output_frame = ctk.CTkFrame(right_frame)
        output_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.output_textbox = ctk.CTkTextbox(
            output_frame,
            font=ctk.CTkFont(family="Courier", size=10),
            wrap="word"
        )
        self.output_textbox.pack(fill="both", expand=True)
    
    def _setup_info_panel(self, parent):
        """Setup info panel"""
        info_panel = ctk.CTkFrame(parent)
        info_panel.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nsew")
        
        ctk.CTkLabel(info_panel, text="Training Tips",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        tips_text = """
💡 Training Tips:

• Batch Size: 8 untuk RTX 3050 4GB (optimal)
• Image Size: 416px hemat VRAM, 640px lebih akurat
• Workers: 2-4 untuk sistem dengan RAM terbatas
• Patience: Naikkan jika training lambat konvergen
• AMP: Aktifkan untuk hemat VRAM (~40%)
• Cache: Disable untuk hemat RAM

⚠️ Important:
• Pastikan data.yaml berisi path dataset yang benar
• Training akan berjalan di background
• Model tersimpan di folder runs/detect/
• Proses training bisa dihentikan kapan saja

🎯 Recommended Settings (RTX 3050):
Batch: 8 | ImgSz: 416 | Workers: 2
        """
        
        ctk.CTkLabel(info_panel, text=tips_text, justify="left",
                    font=ctk.CTkFont(size=11)).pack(pady=10, padx=20, anchor="w")
    
    def _create_param_entry(self, parent, label, default, var_name, pady=5):
        """Helper to create parameter entry"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=pady, padx=20, fill="x")
        
        ctk.CTkLabel(frame, text=label, width=100, anchor="w").pack(side="left")
        var = ctk.StringVar(value=default)
        setattr(self, var_name, var)
        ctk.CTkEntry(frame, textvariable=var, width=100, height=35).pack(side="left", padx=10)
    
    def browse_dataset(self):
        """Browse for dataset file"""
        file_path = filedialog.askopenfilename(
            title="Pilih File data.yaml",
            filetypes=[("YAML files", "*.yaml"), ("All Files", "*.*")]
        )
        if file_path:
            self.dataset_path_var.set(file_path)
    
    def start_training(self):
        """Start training"""
        import os
        
        # Validate dataset
        dataset_path = self.dataset_path_var.get()
        if not os.path.exists(dataset_path):
            messagebox.showerror("Error", f"Dataset tidak ditemukan:\n{dataset_path}")
            return
        
        # Get device info
        import torch
        device_info = "CPU"
        if torch.cuda.is_available():
            device_info = f"GPU: {torch.cuda.get_device_name(0)}"
        
        # Confirm
        if not messagebox.askyesno("Konfirmasi Training",
            f"Mulai training dengan konfigurasi:\n\n"
            f"Model: {self.model_var.get()}\n"
            f"Epochs: {self.epochs_var.get()}\n"
            f"Batch: {self.batch_var.get()}\n"
            f"Image Size: {self.imgsz_var.get()}\n"
            f"Device: {device_info}\n\n"
            f"Training akan berjalan di background.\n"
            f"Lanjutkan?"):
            return
        
        # Prepare parameters
        params = {
            'model': self.model_var.get(),
            'data': dataset_path,
            'epochs': int(self.epochs_var.get()),
            'batch': int(self.batch_var.get()),
            'imgsz': int(self.imgsz_var.get()),
            'workers': int(self.workers_var.get()),
            'patience': int(self.patience_var.get()),
            'cache': self.cache_var.get(),
            'amp': self.amp_var.get(),
            'plots': self.plots_var.get()
        }
        
        # Start training
        success, message = self.training_manager.start_training(
            params,
            self.log_output,
            self.training_finished
        )
        
        if success:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_label.configure(text="Training...", text_color="#f39c12")
            self.output_textbox.delete("1.0", "end")
        else:
            messagebox.showwarning("Warning", message)
    
    def stop_training(self):
        """Stop training"""
        if not messagebox.askyesno("Konfirmasi",
            "Yakin ingin menghentikan training?\n\n"
            "Progress yang sudah berjalan akan hilang!"):
            return
        
        self.training_manager.stop_training()
        self.log_output("⚠️ Training dihentikan oleh user...")
        messagebox.showinfo("Info", "Training akan dihentikan...")
    
    def log_output(self, message):
        """Log output message"""
        self.output_textbox.insert("end", message + "\n")
        self.output_textbox.see("end")
        
        # Parse epoch progress
        if "Epoch" in message or "epoch" in message:
            try:
                import re
                match = re.search(r'(\d+)/(\d+)', message)
                if match:
                    current, total = match.groups()
                    self.epoch_label.configure(text=f"{current}/{total}")
            except:
                pass
    
    def training_finished(self):
        """Called when training finishes"""
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Completed", text_color="#2ecc71")
        
        messagebox.showinfo(
            "Training Complete",
            "✅ Training selesai!\n\n"
            "Model tersimpan di:\n"
            "runs/detect/train_*/weights/best.pt"
        )
    
    def monitor_training_output(self):
        """Monitor training output"""
        try:
            messages = self.training_manager.get_output()
            for message in messages:
                self.log_output(message)
        except:
            pass
        
        # Continue monitoring
        self.tab.after(100, self.monitor_training_output)