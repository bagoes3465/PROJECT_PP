"""
Training Tab UI - Enhanced with Nominal Batch Size
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from Core.constants import EMOJI


class TrainingTab:
    """Training tab UI with real-time monitoring"""
    
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
        
        # === NOMINAL BATCH SIZE (NEW) ===
        nominal_frame = ctk.CTkFrame(params_frame, fg_color="#1a4d2b", corner_radius=8)
        nominal_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(nominal_frame, text="⭐ Nominal Batch Size:",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#2ecc71").pack(pady=(10, 5), padx=20, anchor="w")
        
        nominal_control = ctk.CTkFrame(nominal_frame, fg_color="transparent")
        nominal_control.pack(pady=5, padx=20, fill="x")
        
        self.nominal_batch_var = ctk.StringVar(value="16")
        ctk.CTkEntry(nominal_control, textvariable=self.nominal_batch_var, 
                    width=100, height=35).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(nominal_control, 
                    text="← Effective batch size via gradient accumulation",
                    font=ctk.CTkFont(size=11),
                    text_color="#2ecc71").pack(side="left")
        
        ctk.CTkLabel(nominal_frame, 
                    text="💡 Nominal = Effective learning batch size\n"
                         "   Larger = Better gradients, smoother training",
                    font=ctk.CTkFont(size=10),
                    text_color="gray",
                    justify="left").pack(pady=(0, 10), padx=20, anchor="w")
        
        # Physical Batch (renamed)
        physical_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        physical_frame.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(physical_frame, text="Physical Batch:", 
                    width=120, anchor="w",
                    font=ctk.CTkFont(size=12)).pack(side="left")
        
        self.batch_var = ctk.StringVar(value="8")
        ctk.CTkEntry(physical_frame, textvariable=self.batch_var, 
                    width=80, height=35).pack(side="left", padx=10)
        
        ctk.CTkLabel(physical_frame, 
                    text="← Actual GPU batch (8 for 4GB VRAM)",
                    font=ctk.CTkFont(size=10),
                    text_color="gray").pack(side="left")
        
        # Batch calculation display
        self.batch_calc_label = ctk.CTkLabel(
            params_frame,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#3498db"
        )
        self.batch_calc_label.pack(pady=5, padx=20, anchor="w")
        
        # Update calculation on change
        self.nominal_batch_var.trace_add("write", self._update_batch_calculation)
        self.batch_var.trace_add("write", self._update_batch_calculation)
        self._update_batch_calculation()
        
        # Image size
        imgsz_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        imgsz_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(imgsz_frame, text="Image Size:", width=120, anchor="w").pack(side="left")
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
    
    def _update_batch_calculation(self, *args):
        """Update batch size calculation display"""
        try:
            nominal = int(self.nominal_batch_var.get())
            physical = int(self.batch_var.get())
            accumulate = max(1, round(nominal / physical))
            effective = physical * accumulate
            
            calc_text = (
                f"📊 Calculation: {nominal} (nominal) ÷ {physical} (physical) = "
                f"{accumulate}x accumulation → {effective} effective batch"
            )
            self.batch_calc_label.configure(text=calc_text)
        except:
            self.batch_calc_label.configure(text="")
    
    def _setup_output_panel(self, parent):
        """Setup output panel with enhanced monitoring"""
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(right_frame, text="Training Monitor",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Progress info with real-time metrics
        progress_frame = ctk.CTkFrame(right_frame, fg_color="#2b2b2b", height=160)
        progress_frame.pack(pady=10, padx=20, fill="x")
        progress_frame.pack_propagate(False)
        
        # Create grid for metrics
        metrics_grid = ctk.CTkFrame(progress_frame, fg_color="transparent")
        metrics_grid.pack(expand=True, pady=10)
        
        # Row 1: Status and Epoch
        row1 = ctk.CTkFrame(metrics_grid, fg_color="transparent")
        row1.pack(pady=5)
        
        status_container = ctk.CTkFrame(row1, fg_color="#1a1a1a", corner_radius=8)
        status_container.pack(side="left", padx=10)
        ctk.CTkLabel(status_container, text="Status:", 
                    font=ctk.CTkFont(size=11)).pack(side="left", padx=5, pady=8)
        self.status_label = ctk.CTkLabel(
            status_container, text="Ready",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=5, pady=8)
        
        epoch_container = ctk.CTkFrame(row1, fg_color="#1a1a1a", corner_radius=8)
        epoch_container.pack(side="left", padx=10)
        ctk.CTkLabel(epoch_container, text="Epoch:", 
                    font=ctk.CTkFont(size=11)).pack(side="left", padx=5, pady=8)
        self.epoch_label = ctk.CTkLabel(
            epoch_container, text="0/0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#3498db"
        )
        self.epoch_label.pack(side="left", padx=5, pady=8)
        
        # Row 2: Progress Bar
        progress_bar_container = ctk.CTkFrame(metrics_grid, fg_color="transparent")
        progress_bar_container.pack(pady=5, fill="x", padx=20)
        
        self.progress_bar = ctk.CTkProgressBar(progress_bar_container, height=25)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            progress_bar_container,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.progress_label.pack()
        
        # Row 3: Metrics
        row3 = ctk.CTkFrame(metrics_grid, fg_color="transparent")
        row3.pack(pady=5)
        
        loss_container = ctk.CTkFrame(row3, fg_color="#1a1a1a", corner_radius=8)
        loss_container.pack(side="left", padx=10)
        ctk.CTkLabel(loss_container, text="Loss:", 
                    font=ctk.CTkFont(size=11)).pack(side="left", padx=5, pady=8)
        self.loss_label = ctk.CTkLabel(
            loss_container, text="0.0000",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#e74c3c"
        )
        self.loss_label.pack(side="left", padx=5, pady=8)
        
        map_container = ctk.CTkFrame(row3, fg_color="#1a1a1a", corner_radius=8)
        map_container.pack(side="left", padx=10)
        ctk.CTkLabel(map_container, text="Best mAP:", 
                    font=ctk.CTkFont(size=11)).pack(side="left", padx=5, pady=8)
        self.map_label = ctk.CTkLabel(
            map_container, text="0.0000",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#2ecc71"
        )
        self.map_label.pack(side="left", padx=5, pady=8)
        
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
💡 Nominal Batch Size (NEW!):
• Effective batch size untuk learning
• Larger = Smoother gradients, better convergence
• Recommended: 16-32 untuk egg detection
• GPU akan accumulate gradients otomatis

⚙️ Physical Batch Size:
• Actual batch loaded ke GPU memory
• 8 untuk RTX 3050 4GB (optimal)
• 16 jika VRAM cukup, 4-6 jika OOM

📊 Gradient Accumulation:
• Automatic: Nominal ÷ Physical = Accumulation steps
• Example: 16 ÷ 8 = 2x accumulation
• Training stable seperti batch 16, tapi hemat VRAM!

🎯 Other Settings:
• Image Size: 416px balance speed/accuracy
• Workers: 2-4 untuk sistem dengan RAM terbatas
• Patience: 20+ jika training lambat konvergen
• AMP: Aktifkan untuk hemat VRAM (~40%)

⚠️ Important:
• Monitor progress bar dan metrics real-time
• Loss turun = good, mAP naik = better
• Training dapat dihentikan kapan saja
        """
        
        ctk.CTkLabel(info_panel, text=tips_text, justify="left",
                    font=ctk.CTkFont(size=11)).pack(pady=10, padx=20, anchor="w")
    
    def _create_param_entry(self, parent, label, default, var_name, pady=5):
        """Helper to create parameter entry"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=pady, padx=20, fill="x")
        
        ctk.CTkLabel(frame, text=label, width=120, anchor="w",
                    font=ctk.CTkFont(size=12)).pack(side="left")
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
        
        # Validate batch sizes
        try:
            nominal_batch = int(self.nominal_batch_var.get())
            actual_batch = int(self.batch_var.get())
            
            if nominal_batch < 1 or actual_batch < 1:
                raise ValueError("Batch size must be positive")
            
            if actual_batch > nominal_batch:
                messagebox.showwarning("Warning",
                    f"Physical batch ({actual_batch}) > Nominal batch ({nominal_batch})\n\n"
                    f"Physical batch akan diset sama dengan Nominal.")
                actual_batch = nominal_batch
                self.batch_var.set(str(nominal_batch))
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid batch size: {e}")
            return
        
        # Get device info
        import torch
        device_info = "CPU"
        if torch.cuda.is_available():
            device_info = f"GPU: {torch.cuda.get_device_name(0)}"
        
        # Calculate accumulation
        accumulate = max(1, round(nominal_batch / actual_batch))
        effective = actual_batch * accumulate
        
        # Confirm
        if not messagebox.askyesno("Konfirmasi Training",
            f"Mulai training dengan konfigurasi:\n\n"
            f"Model: {self.model_var.get()}\n"
            f"Epochs: {self.epochs_var.get()}\n"
            f"─────────────────────\n"
            f"Nominal Batch: {nominal_batch}\n"
            f"Physical Batch: {actual_batch}\n"
            f"Accumulation: {accumulate}x\n"
            f"Effective Batch: {effective}\n"
            f"─────────────────────\n"
            f"Image Size: {self.imgsz_var.get()}\n"
            f"Device: {device_info}\n\n"
            f"Training akan berjalan dengan monitoring real-time.\n"
            f"Lanjutkan?"):
            return
        
        # Prepare parameters
        params = {
            'model': self.model_var.get(),
            'data': dataset_path,
            'epochs': int(self.epochs_var.get()),
            'nominal_batch': nominal_batch,  # NEW
            'batch': actual_batch,
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
            self.progress_bar.set(0)
            self.progress_label.configure(text="0%")
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
        """Monitor training output and update metrics"""
        try:
            # Get output messages
            messages = self.training_manager.get_output()
            for message in messages:
                self.log_output(message)
            
            # Update progress metrics
            if self.training_manager.training_running:
                progress = self.training_manager.get_progress()
                
                # Update epoch
                self.epoch_label.configure(
                    text=f"{progress['current_epoch']}/{progress['total_epochs']}"
                )
                
                # Update progress bar
                progress_value = progress['progress'] / 100.0
                self.progress_bar.set(progress_value)
                self.progress_label.configure(text=f"{progress['progress']:.1f}%")
                
                # Update loss
                if progress['current_loss'] > 0:
                    self.loss_label.configure(text=f"{progress['current_loss']:.4f}")
                
                # Update mAP
                if progress['best_map'] > 0:
                    self.map_label.configure(text=f"{progress['best_map']:.4f}")
                    
        except Exception as e:
            pass  # Silently ignore errors
        
        # Continue monitoring
        self.tab.after(100, self.monitor_training_output)