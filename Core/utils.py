"""Utility functions"""
import os
import platform
import threading


def setup_tcl_environment():
    """Setup TCL/TK environment"""
    import sys
    tcl_dir = os.path.join(sys.base_prefix, 'tcl', 'tcl8.6')
    tk_dir = os.path.join(sys.base_prefix, 'tcl', 'tk8.6')
    os.environ['TCL_LIBRARY'] = tcl_dir
    os.environ['TK_LIBRARY'] = tk_dir


def create_directories():
    """Create necessary directories"""
    from Core.constants import REJECTED_IMAGES_FOLDER
    os.makedirs(REJECTED_IMAGES_FOLDER, exist_ok=True)
    os.makedirs("models", exist_ok=True)


def play_alert_sound():
    """Play alert sound based on OS"""
    try:
        system = platform.system()
        if system == "Windows":
            import winsound
            threading.Thread(target=lambda: winsound.Beep(1000, 200), daemon=True).start()
        elif system == "Darwin":
            os.system('afplay /System/Library/Sounds/Ping.aiff &')
        else:
            print('\a')
    except Exception as e:
        print(f"Could not play sound: {e}")


def ambil_keputusan(labels):
    """
    Determine decision: ACCEPT or REJECT
    
    Args:
        labels (list): List of detected labels
        
    Returns:
        str: "ACCEPT" or "REJECT"
    """
    reject_classes = ["crack", "dirty"]
    labels_lower = [label.lower() for label in labels]
    return "REJECT" if any(lbl in reject_classes for lbl in labels_lower) else "ACCEPT"