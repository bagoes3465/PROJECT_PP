import threading
import time
import queue
import gc
import torch
import re
from pathlib import Path
from ultralytics import YOLO


class TrainingManager:
    """YOLO Training Manager - Enhanced with monitoring"""
    
    def __init__(self):
        self.training_running = False
        self.training_thread = None
        self.training_params = {}
        self.output_queue = queue.Queue()
        
        # Training state
        self.current_epoch = 0
        self.total_epochs = 0
        self.current_loss = 0.0
        self.best_map = 0.0
        self.training_progress = 0.0
    
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
        self.current_epoch = 0
        self.total_epochs = params.get('epochs', 100)
        
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
    
    def get_progress(self):
        """Get training progress"""
        return {
            'current_epoch': self.current_epoch,
            'total_epochs': self.total_epochs,
            'progress': self.training_progress,
            'current_loss': self.current_loss,
            'best_map': self.best_map
        }
    
    def _log(self, message):
        """Put message in queue"""
        self.output_queue.put(message)
    
    def _parse_training_output(self, line):
        """Parse training output for progress tracking"""
        try:
            # Parse epoch: "Epoch 12/100"
            epoch_match = re.search(r'(?:Epoch|epoch)\s+(\d+)[/\s]+(\d+)', line)
            if epoch_match:
                self.current_epoch = int(epoch_match.group(1))
                self.total_epochs = int(epoch_match.group(2))
                self.training_progress = (self.current_epoch / self.total_epochs) * 100
            
            # Parse loss: "loss: 0.234"
            loss_match = re.search(r'loss[:\s]+([0-9.]+)', line, re.IGNORECASE)
            if loss_match:
                self.current_loss = float(loss_match.group(1))
            
            # Parse mAP: "mAP50: 0.854" or "metrics/mAP50: 0.854"
            map_match = re.search(r'mAP50[:\s]+([0-9.]+)', line, re.IGNORECASE)
            if map_match:
                map_value = float(map_match.group(1))
                self.best_map = max(self.best_map, map_value)
                
        except Exception as e:
            pass  # Silently ignore parsing errors
    
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
            
            # Calculate actual batch size
            nominal_batch = self.training_params.get('nominal_batch', 16)
            actual_batch = self.training_params.get('batch', 8)
            accumulate = max(1, round(nominal_batch / actual_batch))
            
            self._log("")
            self._log(f"📊 Batch Configuration:")
            self._log(f"   Nominal Batch Size: {nominal_batch}")
            self._log(f"   Actual Batch Size: {actual_batch}")
            self._log(f"   Gradient Accumulation: {accumulate}x")
            self._log(f"   Effective Batch Size: {actual_batch * accumulate}")
            
            # Load model
            self._log("")
            self._log(f"📦 Loading {self.training_params['model']}...")
            model = YOLO(self.training_params['model'])
            
            # Training
            self._log("")
            self._log(f"🚀 Starting training with optimized settings...")
            self._log(f"📈 Epochs: {self.training_params['epochs']}")
            self._log(f"🖼️  Image Size: {self.training_params['imgsz']}")
            self._log(f"👷 Workers: {self.training_params['workers']}")
            self._log(f"⏸️  Patience: {self.training_params['patience']}")
            self._log("="*70)
            self._log("")
            
            # Custom callback for progress tracking
            def on_train_batch_end(trainer):
                """Called after each training batch"""
                if not self.training_running:
                    trainer.stop = True
                    return
                
                # Log progress
                if hasattr(trainer, 'epoch') and hasattr(trainer, 'epochs'):
                    self.current_epoch = trainer.epoch + 1
                    self.total_epochs = trainer.epochs
                    self.training_progress = (self.current_epoch / self.total_epochs) * 100
                    
                    # Log loss if available
                    try:
                        if hasattr(trainer, 'loss_items') and trainer.loss_items is not None:
                            loss_items = trainer.loss_items
                            
                            # Handle different loss formats
                            if hasattr(loss_items, 'item'):
                                # Single tensor
                                self.current_loss = loss_items.item()
                            elif isinstance(loss_items, (list, tuple)):
                                # List/tuple of tensors
                                total = 0
                                for item in loss_items:
                                    if hasattr(item, 'item'):
                                        total += item.item()
                                    else:
                                        total += float(item)
                                self.current_loss = total
                            else:
                                self.current_loss = float(loss_items)
                    except:
                        pass  # Ignore loss parsing errors
            
            def on_train_epoch_end(trainer):
                """Called after each training epoch"""
                if not self.training_running:
                    trainer.stop = True
                    return
                
                # Log epoch summary
                epoch_msg = f"\n{'='*70}\n"
                epoch_msg += f"Epoch {self.current_epoch}/{self.total_epochs} Complete"
                epoch_msg += f"\n{'='*70}\n"
                self._log(epoch_msg)
                
                # Log metrics if available
                try:
                    if hasattr(trainer, 'metrics') and trainer.metrics:
                        metrics = trainer.metrics
                        self._log(f"📊 Metrics:")
                        
                        # Handle different metric formats
                        if hasattr(metrics, 'box'):
                            # Ultralytics format
                            if hasattr(metrics.box, 'map50'):
                                map50 = metrics.box.map50
                                if hasattr(map50, 'item'):
                                    map50 = map50.item()
                                self._log(f"   mAP50: {map50:.4f}")
                                self.best_map = max(self.best_map, float(map50))
                            
                            if hasattr(metrics.box, 'map'):
                                map_val = metrics.box.map
                                if hasattr(map_val, 'item'):
                                    map_val = map_val.item()
                                self._log(f"   mAP50-95: {map_val:.4f}")
                        elif isinstance(metrics, dict):
                            # Dictionary format
                            if 'metrics/mAP50' in metrics:
                                map50 = float(metrics['metrics/mAP50'])
                                self._log(f"   mAP50: {map50:.4f}")
                                self.best_map = max(self.best_map, map50)
                except Exception as e:
                    pass  # Ignore metric parsing errors
            
            # Add callbacks
            model.add_callback("on_train_batch_end", on_train_batch_end)
            model.add_callback("on_train_epoch_end", on_train_epoch_end)
            
            # Alternative: Monitor via epoch start callback (more reliable)
            def on_train_epoch_start(trainer):
                """Called at start of each epoch"""
                if not self.training_running:
                    trainer.stop = True
                    return
                
                if hasattr(trainer, 'epoch') and hasattr(trainer, 'epochs'):
                    self.current_epoch = trainer.epoch + 1
                    self.total_epochs = trainer.epochs
                    self.training_progress = (self.current_epoch / self.total_epochs) * 100
                    
                    # Log epoch start
                    self._log(f"\n▶️  Starting Epoch {self.current_epoch}/{self.total_epochs}")
            
            model.add_callback("on_train_epoch_start", on_train_epoch_start)
            
            # Validation end callback for metrics
            def on_fit_epoch_end(trainer):
                """Called after validation at epoch end"""
                if not self.training_running:
                    trainer.stop = True
                    return
                
                try:
                    # Get metrics from trainer
                    if hasattr(trainer, 'metrics'):
                        metrics = trainer.metrics
                        if metrics and hasattr(metrics, 'results_dict'):
                            results = metrics.results_dict
                            
                            # Extract mAP50
                            if 'metrics/mAP50(B)' in results:
                                map50 = float(results['metrics/mAP50(B)'])
                                self.best_map = max(self.best_map, map50)
                            elif 'metrics/mAP50' in results:
                                map50 = float(results['metrics/mAP50'])
                                self.best_map = max(self.best_map, map50)
                    
                    # Also try to get loss from validator
                    if hasattr(trainer, 'loss'):
                        try:
                            loss_val = trainer.loss
                            if hasattr(loss_val, 'item'):
                                self.current_loss = loss_val.item()
                            else:
                                self.current_loss = float(loss_val)
                        except:
                            pass
                            
                except Exception as e:
                    pass  # Ignore errors
            
            model.add_callback("on_fit_epoch_end", on_fit_epoch_end)
            
            # TRAINING CONFIG - OPTIMIZED FOR 4GB VRAM
            self._log("🔧 Initializing training configuration...")
            
            results = model.train(
                # Dataset
                data=str(data_path),
                
                # === CRITICAL: VRAM OPTIMIZATION ===
                epochs=self.training_params['epochs'],
                batch=actual_batch,  # Physical batch size
                imgsz=self.training_params['imgsz'],
                device=device,
                workers=self.training_params['workers'],
                
                # === GRADIENT ACCUMULATION ===
                nbs=nominal_batch,  # Nominal batch size for gradient accumulation
                
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
            self._log(f"📊 Final Results:")
            self._log(f"   Best mAP50: {self.best_map:.4f}")
            self._log(f"   Total Epochs: {self.current_epoch}/{self.total_epochs}")
            
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