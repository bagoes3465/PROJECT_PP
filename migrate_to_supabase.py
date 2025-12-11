"""
Migrate CSV data to Supabase
"""
from Core.supabase_database import get_supabase_db
from pathlib import Path

def migrate():
    print("="*60)
    print("MIGRATION: CSV → SUPABASE")
    print("="*60)
    
    csv_file = "E:\PROJECT_PP\Data Folder\log_deteksi.csv"
    
    if not Path(csv_file).exists():
        print(f"\n⚠️ File {csv_file} tidak ditemukan")
        print("Tidak ada data untuk dimigrate")
        return
    
    print(f"\n📂 Found: {csv_file}")
    response = input("Migrate to Supabase? (y/n): ")
    
    if response.lower() != 'y':
        print("❌ Migration cancelled")
        return
    
    try:
        db = get_supabase_db()
        count = db.migrate_from_csv(csv_file)
        
        if count > 0:
            print(f"\n✅ Successfully migrated {count} records!")
            
            # Backup CSV
            backup_file = f"log_deteksi_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            Path(csv_file).rename(backup_file)
            print(f"📦 CSV backed up to: {backup_file}")
        else:
            print("\n⚠️ No records migrated")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")

if __name__ == "__main__":
    from datetime import datetime
    migrate()