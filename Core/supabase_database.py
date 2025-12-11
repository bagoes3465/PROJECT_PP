"""
Supabase Online Database Manager
Cloud-based storage untuk Egg Sorter
"""
from supabase import create_client, Client
from datetime import datetime
from typing import List, Dict, Optional
import threading
import os
from dotenv import load_dotenv

class SupabaseDatabase:
    """Online database manager menggunakan Supabase"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError(
                "⚠️ Supabase credentials tidak ditemukan!\n"
                "Buat file .env dengan:\n"
                "  SUPABASE_URL=https://xxxxx.supabase.co\n"
                "  SUPABASE_KEY=eyJhbGc..."
            )
        
        try:
            self.client: Client = create_client(self.url, self.key)
            print("✅ Connected to Supabase")
            self._test_connection()
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            raise
        
        self.lock = threading.Lock()
    
    def _test_connection(self):
        """Test koneksi dengan query sederhana"""
        try:
            response = self.client.table('detections').select("count").limit(1).execute()
            print(f"✅ Supabase connection test: OK")
        except Exception as e:
            print(f"⚠️ Connection test failed: {e}")
    
    # ==================== INSERT OPERATIONS ====================
    
    def insert_detection(self, 
                        waktu: str,
                        sumber: str,
                        kelas: str,
                        keputusan: str,
                        confidence: float,
                        inference_time: float,
                        saved_path: str = "N/A",
                        object_id: str = None,
                        fps: float = None,
                        serial_sent: bool = False,
                        centroid_x: int = None,
                        centroid_y: int = None) -> Optional[Dict]:
        """Insert detection ke Supabase"""
        with self.lock:
            try:
                data = {
                    "waktu": waktu,
                    "sumber": sumber,
                    "kelas_terdeteksi": kelas,
                    "keputusan": keputusan,
                    "confidence": confidence,
                    "inference_time_ms": inference_time,
                    "saved_path": saved_path,
                    "object_id": object_id,
                    "fps": fps,
                    "serial_sent": serial_sent,
                    "centroid_x": centroid_x,
                    "centroid_y": centroid_y
                }
                
                response = self.client.table('detections').insert(data).execute()
                
                if response.data:
                    return response.data[0]
                return None
                
            except Exception as e:
                print(f"❌ Error inserting to Supabase: {e}")
                return None
    
    # ==================== GET OPERATIONS ====================
    
    def get_all_detections(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get detections dengan pagination"""
        try:
            response = self.client.table('detections')\
                .select("*")\
                .order('waktu', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Error getting detections: {e}")
            return []
    
    def get_detections_by_date(self, 
                               start_date: str, 
                               end_date: str = None,
                               limit: int = 1000) -> List[Dict]:
        """Get detections by date range"""
        try:
            query = self.client.table('detections').select("*")
            
            query = query.gte('waktu', start_date)
            
            if end_date:
                query = query.lte('waktu', end_date)
            
            response = query.order('waktu', desc=True).limit(limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Error getting detections by date: {e}")
            return []
    
    def get_detections_by_decision(self, 
                                   keputusan: str,
                                   limit: int = 100) -> List[Dict]:
        """Get detections filtered by decision (ACCEPT/REJECT)"""
        try:
            response = self.client.table('detections')\
                .select("*")\
                .eq('keputusan', keputusan)\
                .order('waktu', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Error getting detections by decision: {e}")
            return []
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> Dict:
        """Get overall statistics"""
        try:
            # Count total
            total_response = self.client.table('detections')\
                .select("*", count='exact')\
                .execute()
            total = total_response.count if hasattr(total_response, 'count') else 0
            
            # Count accepts
            accept_response = self.client.table('detections')\
                .select("*", count='exact')\
                .eq('keputusan', 'ACCEPT')\
                .execute()
            accept = accept_response.count if hasattr(accept_response, 'count') else 0
            
            # Count rejects
            reject_response = self.client.table('detections')\
                .select("*", count='exact')\
                .eq('keputusan', 'REJECT')\
                .execute()
            reject = reject_response.count if hasattr(reject_response, 'count') else 0
            
            return {
                'total': total,
                'accept': accept,
                'reject': reject,
                'reject_rate': (reject / total * 100) if total > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {'total': 0, 'accept': 0, 'reject': 0, 'reject_rate': 0}
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """Get daily statistics"""
        try:
            response = self.client.table('daily_stats')\
                .select("*")\
                .order('date', desc=True)\
                .limit(days)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Error getting daily stats: {e}")
            return []
    
    def get_hourly_stats_today(self) -> List[Dict]:
        """Get hourly stats for today"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            response = self.client.rpc('get_hourly_stats', {
                'target_date': today
            }).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Error getting hourly stats: {e}")
            return []
    
    # ==================== REALTIME SUBSCRIPTIONS ====================
    
    def subscribe_to_detections(self, callback):
        """Subscribe to realtime detection updates"""
        try:
            def on_insert(payload):
                callback(payload['new'])
            
            # Subscribe to INSERT events
            self.client.table('detections')\
                .on('INSERT', on_insert)\
                .subscribe()
            
            print("✅ Subscribed to realtime updates")
            
        except Exception as e:
            print(f"❌ Error subscribing: {e}")
    
    # ==================== EXPORT ====================
    
    def export_to_csv(self, csv_path: str, limit: int = 10000):
        """Export data to CSV"""
        import pandas as pd
        
        try:
            detections = self.get_all_detections(limit=limit)
            
            if not detections:
                print("⚠️ No data to export")
                return False
            
            df = pd.DataFrame(detections)
            df.to_csv(csv_path, index=False)
            print(f"✅ Exported {len(detections)} records to {csv_path}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    # ==================== MIGRATION ====================
    
    def migrate_from_csv(self, csv_path: str) -> int:
        """Migrate existing CSV data to Supabase"""
        import pandas as pd
        
        try:
            df = pd.read_csv(csv_path)
            migrated = 0
            failed = 0
            
            print(f"📤 Starting migration of {len(df)} records...")
            
            for idx, row in df.iterrows():
                try:
                    result = self.insert_detection(
                        waktu=row.get('waktu', datetime.now().isoformat()),
                        sumber=row.get('sumber', 'unknown'),
                        kelas=row.get('kelas_terdeteksi', ''),
                        keputusan=row.get('keputusan', 'ACCEPT'),
                        confidence=float(row.get('confidence', 0)),
                        inference_time=float(row.get('inference_time_ms', 0)),
                        saved_path=row.get('saved_path', 'N/A')
                    )
                    
                    if result:
                        migrated += 1
                        if (migrated % 10) == 0:
                            print(f"  Progress: {migrated}/{len(df)}")
                    else:
                        failed += 1
                        
                except Exception as e:
                    print(f"  ⚠️ Failed row {idx}: {e}")
                    failed += 1
                    continue
            
            print(f"\n✅ Migration complete!")
            print(f"  Success: {migrated}")
            print(f"  Failed: {failed}")
            
            return migrated
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return 0
    
    # ==================== DELETE OPERATIONS ====================
    
    def delete_old_records(self, days: int = 90) -> int:
        """Delete records older than N days"""
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            response = self.client.table('detections')\
                .delete()\
                .lt('waktu', cutoff_date.isoformat())\
                .execute()
            
            count = len(response.data) if response.data else 0
            print(f"🗑️ Deleted {count} old records")
            return count
            
        except Exception as e:
            print(f"❌ Error deleting records: {e}")
            return 0


# ==================== SINGLETON ====================
_supabase_db = None

def get_supabase_db() -> SupabaseDatabase:
    """Get singleton Supabase instance"""
    global _supabase_db
    if _supabase_db is None:
        _supabase_db = SupabaseDatabase()
    return _supabase_db