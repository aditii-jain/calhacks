#!/usr/bin/env python3
"""Cleanup script to remove test data from the database"""

from supabase import create_client
from config import settings

def cleanup_test_data():
    """Remove all test data from the classified_data table"""
    print("🧹 Crisis-MMD Test Data Cleanup")
    print("=" * 40)
    
    if not settings.supabase_url or not settings.supabase_service_key:
        print("❌ Supabase credentials not configured")
        return False
    
    try:
        client = create_client(settings.supabase_url, settings.supabase_service_key)
        print("✅ Connected to Supabase")
        
        # Get current count
        response = client.table('classified_data').select('id', count='exact').execute()
        current_count = response.count or 0
        print(f"📊 Current records in database: {current_count}")
        
        if current_count == 0:
            print("✅ Database is already empty")
            return True
        
        # Confirm deletion
        print(f"\n⚠️  This will delete ALL {current_count} records from the classified_data table.")
        confirm = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y']:
            print("❌ Cleanup cancelled")
            return False
        
        # Delete all records
        print("🗑️  Deleting all records...")
        delete_response = client.table('classified_data').delete().neq('id', 0).execute()
        
        # Verify deletion
        final_response = client.table('classified_data').select('id', count='exact').execute()
        final_count = final_response.count or 0
        
        if final_count == 0:
            print("✅ All test data removed successfully")
            print(f"📊 Records deleted: {current_count}")
            return True
        else:
            print(f"⚠️  Some records may remain: {final_count}")
            return False
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def main():
    """Main cleanup process"""
    success = cleanup_test_data()
    
    if success:
        print("\n🎉 Cleanup completed!")
        print("\n🔄 Next steps:")
        print("   1. Run setup_supabase.py if needed")
        print("   2. Start fresh with your real data")
    else:
        print("\n❌ Cleanup failed - please check the errors above")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 