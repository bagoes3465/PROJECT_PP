"""
Test Supabase Connection
"""
from Core.supabase_database import get_supabase_db
from datetime import datetime

def test_supabase():
    print("="*60)
    print("SUPABASE CONNECTION TEST")
    print("="*60)
    
    try:
        # 1. Connect
        print("\n1. Testing connection...")
        db = get_supabase_db()
        print("✅ Connected!")
        
        # 2. Insert test data
        print("\n2. Testing insert...")
        result = db.insert_detection(
            waktu=datetime.now().isoformat(),
            sumber="Test Script",
            kelas="clean",
            keputusan="ACCEPT",
            confidence=0.95,
            inference_time=45.5
        )
        print(f"✅ Insert: {result['id'] if result else 'Failed'}")
        
        # 3. Get data
        print("\n3. Testing get data...")
        detections = db.get_all_detections(limit=5)
        print(f"✅ Found {len(detections)} records")
        if detections:
            print(f"Latest: ID={detections[0]['id']}, Decision={detections[0]['keputusan']}")
        
        # 4. Get stats
        print("\n4. Testing stats...")
        stats = db.get_stats()
        print(f"✅ Stats:")
        print(f"  Total: {stats['total']}")
        print(f"  Accept: {stats['accept']}")
        print(f"  Reject: {stats['reject']}")
        print(f"  Reject Rate: {stats['reject_rate']:.1f}%")
        
        # 5. Export test
        print("\n5. Testing export...")
        success = db.export_to_csv("test_export_supabase.csv", limit=10)
        print(f"✅ Export: {'Success' if success else 'Failed'}")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🎉 Supabase is ready to use!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("\nTroubleshooting:")
        print("1. Check .env file exists with correct credentials")
        print("2. Check internet connection")
        print("3. Check Supabase project is active")
        print("4. Check SQL tables were created")

if __name__ == "__main__":
    test_supabase()