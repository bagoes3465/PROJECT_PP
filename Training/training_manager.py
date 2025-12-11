import threading
import time
import queue
import gc
import torch
from pathlib import Path
from ultralytics import YOLO


class TrainingManager:
    """YOLO Training Manager"""
    
    def __init__(self):
        self.training_running = False
        self.training_thread = None
        self.training_params = {}
        self.output_queue = queue.Queue()
    
    def start_training(self, params, log_callback, finish_callback):
        """
        Start YOLO training
        
        Args:
            params (dict): Training parameters
            log_callback (callable): Function to log messages
            finish_callback (callable): Function to call when training finishes
        """
        if self.training_running:
            return False, "Training sudah berjalan!"
        
        self.training_params = params
        self.training_running = True
        
        self.training_thread = threading.Thread(
            target=self._training_worker,
            args=(log_callback, finish_callback),
            daemon=True
        )
        self.training_thread.start()
        
        return True, "Training started"
    
    def stop_training(self):
        """Stop training"""
        self.training_running = False
        return True
    
    def _log(self, message):
        """Put message in queue"""
        self.output_queue.put(message)
    
    def _training_worker(self, log_callback, finish_callback):
        """Worker thread for training - OPTIMIZED FOR RTX 3050 4GB"""
        try:
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
            self._log("="*70)
            self._log("YOLO11 TRAINING - OPTIMIZED FOR RTX 3050 4GB")
            self._log("="*70)
            
            # GPU Check
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                vram_total = torch.cuda.get_device_properties(0).total_memory / 1e9
                self._log("")
                self._log(f"🎮 GPU: {gpu_name}")
                self._log(f"💾 VRAM: {vram_total:.2f} GB")
                device = 0
            else:
                self._log("")
                self._log("⚠️ Using CPU")
                device = "cpu"
            
            # Paths
            data_path = Path(self.training_params['data'])
            project_path = Path(r"Data Folder\runs\detect")
            
            # Load model
            self._log("")
            self._log(f"📦 Loading YOLOv11n model...")
            model = YOLO(self.training_params['model'])
            
            # Training
            self._log("")
            self._log(f"🚀 Starting training with optimized settings...")
            self._log("="*70)
            self._log("")
            
            # TRAINING CONFIG - OPTIMIZED FOR 4GB VRAM
            results = model.train(
                # Dataset
                data=str(data_path),
                
                # === CRITICAL: VRAM OPTIMIZATION ===
                epochs=self.training_params['epochs'],
                batch=self.training_params['batch'],
                imgsz=self.training_params['imgsz'],
                device=device,
                workers=self.training_params['workers'],
                
                # === PERFORMANCE ===
                cache=self.training_params['cache'],
                amp=self.training_params['amp'],
                close_mosaic=0,
                
                # === OPTIMIZER ===
                optimizer='SGD',       # SGD lebih hemat VRAM
                lr0=0.01,
                lrf=0.01,
                momentum=0.937,
                weight_decay=0.0005,
                warmup_epochs=3,
                warmup_momentum=0.8,
                
                # === AUGMENTATION ===
                augment=True,
                hsv_h=0.015,
                hsv_s=0.7,
                hsv_v=0.4,
                degrees=0.0,
                translate=0.1,
                scale=0.5,
                fliplr=0.5,
                mosaic=0.5,
                mixup=0.0,
                copy_paste=0.0,
                
                # === VALIDATION ===
                val=True,
                patience=self.training_params['patience'],
                
                # === SAVING ===
                save=True,
                save_period=10,
                
                # === OUTPUT ===
                project=str(project_path),
                name=f"yolo11n_telur_{time.strftime('%Y%m%d_%H%M%S')}",
                exist_ok=True,
                verbose=True,
                plots=self.training_params['plots']
            )
            
            self._log("")
            self._log("="*70)
            self._log("✅ TRAINING COMPLETED!")
            self._log("="*70)
            
            # Cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
        except Exception as e:
            self._log("")
            self._log(f"❌ ERROR: {str(e)}")
            import traceback
            self._log(traceback.format_exc())
        
        finally:
            # Cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
            self.training_running = False
            finish_callback()
    
    def get_output(self):
        """Get all pending output messages"""
        messages = []
        try:
            while True:
                messages.append(self.output_queue.get_nowait())
        except queue.Empty:
            pass
        return messages