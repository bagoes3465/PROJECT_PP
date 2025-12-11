"""
Standalone YOLO Training Script
Optimized for RTX 3050 4GB VRAM

Usage:
    python train_standalone.py
    
Or customize parameters:
    python train_standalone.py --epochs 150 --batch 16 --imgsz 640
"""

import argparse
import time
import gc
import torch
from pathlib import Path
from ultralytics import YOLO


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='YOLO11 Training for Egg Sorting')
    
    # Dataset
    parser.add_argument('--data', type=str, 
                       default=r'E:\PROYEK_KLASIFIKASI_TELUR\dataset\datav11\data.yaml',
                       help='Path to data.yaml')
    
    # Model
    parser.add_argument('--model', type=str, default='yolo11n.pt',
                       choices=['yolo11n.pt', 'yolo11s.pt', 'yolo11m.pt'],
                       help='Base model to use')
    
    # Training parameters
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of epochs')
    parser.add_argument('--batch', type=int, default=8,
                       help='Batch size (8 for 4GB VRAM)')
    parser.add_argument('--imgsz', type=int, default=416,
                       help='Image size (416 optimal for RTX 3050)')
    parser.add_argument('--workers', type=int, default=2,
                       help='Number of workers')
    parser.add_argument('--patience', type=int, default=20,
                       help='Early stopping patience')
    
    # Performance
    parser.add_argument('--cache', action='store_true',
                       help='Cache images (uses more RAM)')
    parser.add_argument('--amp', type=bool, default=True,
                       help='Use Automatic Mixed Precision')
    parser.add_argument('--device', type=str, default='0',
                       help='Device: 0 for GPU, cpu for CPU')
    
    # Output
    parser.add_argument('--project', type=str,
                       default=r'E:\PROYEK_KLASIFIKASI_TELUR\runs\detect',
                       help='Project directory')
    parser.add_argument('--name', type=str, default=None,
                       help='Experiment name (auto-generated if None)')
    parser.add_argument('--plots', type=bool, default=True,
                       help='Generate plots')
    
    return parser.parse_args()


def print_system_info():
    """Print system information"""
    print("\n" + "="*70)
    print("YOLO11 TRAINING - SYSTEM INFO")
    print("="*70)
    
    # CUDA info
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1e9
        vram_free = torch.cuda.memory_reserved(0) / 1e9
        print(f"\n🎮 GPU: {gpu_name}")
        print(f"💾 VRAM Total: {vram_total:.2f} GB")
        print(f"💾 VRAM Free: {vram_free:.2f} GB")
        print(f"✅ CUDA Version: {torch.version.cuda}")
        device = 0
    else:
        print("\n⚠️  CUDA not available - Using CPU")
        print("⚠️  Training will be VERY slow!")
        device = "cpu"
    
    print(f"\n🐍 PyTorch: {torch.__version__}")
    print("="*70 + "\n")
    
    return device


def train(args):
    """Main training function"""
    
    # Clear GPU memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()
    
    # Print system info
    device = print_system_info()
    
    # Override device if specified
    if args.device.lower() == 'cpu':
        device = 'cpu'
    
    # Validate dataset
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ ERROR: Dataset not found at {data_path}")
        print("Please check the path to data.yaml")
        return
    
    print(f"📁 Dataset: {data_path}")
    print(f"📦 Model: {args.model}")
    print(f"🔢 Epochs: {args.epochs}")
    print(f"📊 Batch Size: {args.batch}")
    print(f"📐 Image Size: {args.imgsz}")
    print(f"👷 Workers: {args.workers}")
    print(f"⏸️  Patience: {args.patience}")
    print(f"⚡ AMP: {args.amp}")
    print(f"💾 Cache: {args.cache}")
    print(f"🖥️  Device: {device}")
    print("\n" + "="*70)
    
    # Confirm
    response = input("\n▶️  Start training? (y/n): ")
    if response.lower() != 'y':
        print("❌ Training cancelled")
        return
    
    # Load model
    print(f"\n📦 Loading {args.model}...")
    model = YOLO(args.model)
    
    # Generate experiment name
    if args.name is None:
        args.name = f"yolo11n_telur_{time.strftime('%Y%m%d_%H%M%S')}"
    
    # Training configuration
    print(f"\n🚀 Starting training: {args.name}")
    print("="*70 + "\n")
    
    try:
        results = model.train(
            # Dataset
            data=str(data_path),
            
            # === CRITICAL: VRAM OPTIMIZATION ===
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
            device=device,
            workers=args.workers,
            
            # === PERFORMANCE ===
            cache=args.cache,
            amp=args.amp,
            close_mosaic=0,
            
            # === OPTIMIZER (Optimized for limited VRAM) ===
            optimizer='SGD',       # SGD uses less VRAM than AdamW
            lr0=0.01,             # Initial learning rate
            lrf=0.01,             # Final learning rate
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
            warmup_momentum=0.8,
            
            # === AUGMENTATION ===
            augment=True,
            hsv_h=0.015,          # Hue augmentation
            hsv_s=0.7,            # Saturation augmentation
            hsv_v=0.4,            # Value augmentation
            degrees=0.0,          # Rotation
            translate=0.1,        # Translation
            scale=0.5,            # Scale
            fliplr=0.5,           # Horizontal flip
            mosaic=0.5,           # Mosaic augmentation
            mixup=0.0,            # Mixup (disabled for VRAM)
            copy_paste=0.0,       # Copy-paste (disabled)
            
            # === VALIDATION ===
            val=True,
            patience=args.patience,
            
            # === SAVING ===
            save=True,
            save_period=10,       # Save checkpoint every 10 epochs
            
            # === OUTPUT ===
            project=args.project,
            name=args.name,
            exist_ok=True,
            verbose=True,
            plots=args.plots
        )
        
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📁 Results saved to: {args.project}/{args.name}")
        print(f"🏆 Best model: {args.project}/{args.name}/weights/best.pt")
        print(f"📊 Metrics: {args.project}/{args.name}/results.csv")
        
        if args.plots:
            print(f"📈 Plots: {args.project}/{args.name}/")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print("Progress has been saved")
        
    except Exception as e:
        print(f"\n❌ ERROR during training:")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up GPU memory...")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        print("✅ Cleanup complete\n")


def main():
    """Main entry point"""
    args = parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          🥚 EGG SORTER - YOLO11 TRAINING SCRIPT 🥚          ║
    ║                                                              ║
    ║              Optimized for RTX 3050 4GB VRAM                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    train(args)
    
    print("\n" + "="*70)
    print("🎉 Training script finished!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()