from ultralytics import YOLO
from pathlib import Path
from tkinter import filedialog, messagebox
import torch

MODEL_PATH = Path(r"Data Folder\models\best.pt")


class ModelManager:
    """YOLO model manager"""
    def __init__(self):
        self.model = None
        self.cuda_available = False
    
    def load(self):
        try:
            model_file = MODEL_PATH
            if not model_file.exists():
                messagebox.showwarning("Model Not Found", 
                    f"Model tidak ditemukan di:\n{MODEL_PATH.absolute()}\n\n"
                    "Silakan pilih file model YOLO (.pt)")
                
                model_path = filedialog.askopenfilename(
                    title="Pilih File Model YOLO",
                    filetypes=[("PyTorch Model", "*.pt"), ("All Files", "*.*")]
                )
                if not model_path:
                    messagebox.showerror("Error", "Model tidak dipilih. Aplikasi akan ditutup.")
                    return False
                model_file = Path(model_path)
            
            print(f"Loading model from: {model_file.absolute()}")
            self.model = YOLO(str(model_file))
            print(f"✅ Model loaded successfully")
            print(f"✅ Detected classes: {self.model.names}")
            
            self.cuda_available = torch.cuda.is_available()
            if self.cuda_available:
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                print(f"✅ CUDA available: {gpu_name} ({gpu_memory:.1f}GB)")
            else:
                print(f"ℹ️ CUDA not available, using CPU only")
            
            return True
        except Exception as e:
            messagebox.showerror("Error Loading Model",
                f"Gagal memuat model YOLO:\n{str(e)}")
            return False
    
    def predict(self, image, conf, device):
        return self.model.predict(image, verbose=False, device=device, conf=conf, half=False)