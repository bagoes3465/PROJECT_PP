import pandas as pd
import os
import threading

LOG_FILE = "log_deteksi.csv"


class LogManager:
    """Log management"""
    def __init__(self):
        self.log_deteksi = []
        self.lock = threading.Lock()
    
    def load(self):
        try:
            df = pd.read_csv(LOG_FILE)
            self.log_deteksi = df.to_dict(orient="records")
            print(f"✅ Loaded {len(self.log_deteksi)} log entries")
            return self.log_deteksi
        except FileNotFoundError:
            print("No existing log file found")
            return []
        except Exception as e:
            print(f"Error loading log: {e}")
            return []
    
    def save_append(self, log_data):
        try:
            with self.lock:
                df_new = pd.DataFrame(log_data)
                df_new.to_csv(LOG_FILE, mode='a', index=False, 
                             header=not os.path.exists(LOG_FILE))
        except Exception as e:
            print(f"Error saving log: {e}")
    
    def add_entry(self, entry):
        with self.lock:
            self.log_deteksi.append(entry)
    
    def reset(self):
        with self.lock:
            self.log_deteksi = []
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)