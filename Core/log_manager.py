"""
Log Manager with Supabase Online Database
"""
import threading
from typing import List, Dict
from Core.supabase_database import get_supabase_db


class LogManager:
    """Log management dengan Supabase backend"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self._cache = []
        self._cache_size = 100
        
        try:
            self.db = get_supabase_db()
            print("✅ LogManager connected to Supabase")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            print("⚠️ App akan jalan tapi tanpa database!")
            self.db = None
    
    def load(self) -> List[Dict]:
        """Load recent logs dari Supabase"""
        if not self.db:
            return []
        
        try:
            detections = self.db.get_all_detections(limit=self._cache_size)
            self._cache = detections
            print(f"✅ Loaded {len(self._cache)} logs from Supabase")
            return self._cache
            
        except Exception as e:
            print(f"❌ Error loading logs: {e}")
            return []
    
    def save_append(self, log_data: List[Dict]):
        """Save logs to Supabase (real-time)"""
        if not self.db:
            print("⚠️ Database not available, skipping save")
            return
        
        # Supabase insert sudah dilakukan di add_entry
        # Method ini keep untuk backward compatibility
        pass
    
    def add_entry(self, entry: Dict):
        """Add log entry dan save ke Supabase"""
        with self.lock:
            # Add to cache
            self._cache.append(entry)
            if len(self._cache) > self._cache_size:
                self._cache.pop(0)
            
            # Save to Supabase (real-time)
            if self.db:
                try:
                    self.db.insert_detection(
                        waktu=entry.get('waktu', ''),
                        sumber=entry.get('sumber', ''),
                        kelas=entry.get('kelas_terdeteksi', ''),
                        keputusan=entry.get('keputusan', ''),
                        confidence=float(entry.get('confidence', 0)),
                        inference_time=float(entry.get('inference_time_ms', 0)),
                        saved_path=entry.get('saved_path', 'N/A'),
                        object_id=entry.get('object_id'),
                        fps=float(entry.get('fps', 0)) if entry.get('fps') else None,
                        serial_sent=entry.get('serial_sent') == 'Yes'
                    )
                except Exception as e:
                    print(f"⚠️ Failed to save to Supabase: {e}")
    
    def reset(self):
        """Clear cache only (tidak delete dari database)"""
        with self.lock:
            self._cache = []
    
    def get_stats_from_db(self):
        """Get stats dari Supabase"""
        if not self.db:
            return {'total': 0, 'accept': 0, 'reject': 0}
        
        try:
            return self.db.get_stats()
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {'total': 0, 'accept': 0, 'reject': 0}
    
    @property
    def log_deteksi(self):
        """Get cached logs"""
        return self._cache