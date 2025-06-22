#!/usr/bin/env python3
"""
Setup script for mock_twitter_posts table in Supabase
Run this once to create the table for storing Mock Twitter posts
"""

import os
import sys
from datetime import datetime

# Simple fallback configuration for when backend config is not available
class SimpleSettings:
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_service_key = os.environ.get("SUPABASE_SERVICE_KEY")

# Add the parent backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, backend_path)  # Insert at beginning to prioritize our config

try:
    # Try to import supabase first
    from supabase import create_client
    
    # Try to import our backend config
    try:
        import config
        settings = config.settings
        print("✅ Backend config loaded successfully")
    except ImportError as backend_import_error:
        print(f"⚠️  Backend config not available: {backend_import_error}")
        print("   Using simple environment-based config")
        settings = SimpleSettings()
    
    print("✅ Supabase integration available")
except ImportError as e:
    print(f"❌ Supabase not available: {e}")
    print("Please ensure you have supabase-py installed:")
    print("pip install supabase")
    print("\n💡 Note: You can skip Supabase setup and use JSON-only mode")
    print("   The Mock Twitter interface works perfectly without Supabase!")
    sys.exit(1)

def create_mock_twitter_table():
    """Create the mock_twitter_posts table in Supabase"""
    
    print("🚨 Mock Twitter Posts Table Setup")
    print("=" * 40)
    
    # Check configuration
    if not settings.supabase_url or not settings.supabase_service_key:
        print("❌ Supabase credentials not configured")
        print("Please check your .env file has:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_KEY")
        return False
    
    try:
        # Create client
        client = create_client(settings.supabase_url, settings.supabase_service_key)
        print("✅ Connected to Supabase")
        
        # Check if table already exists
        try:
            response = client.table('mock_twitter_posts').select('id').limit(1).execute()
            print("✅ Table 'mock_twitter_posts' already exists")
            
            # Show current count
            count_response = client.table('mock_twitter_posts').select('id', count='exact').execute()
            record_count = count_response.count or 0
            print(f"📊 Current records: {record_count}")
            
            return True
            
        except Exception as e:
            error_str = str(e).lower()
            if "does not exist" in error_str or "relation" in error_str:
                print("📋 Table does not exist - needs to be created manually")
                print_manual_instructions()
                return True
            else:
                print(f"⚠️  Error checking table: {e}")
                return False
    
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

def print_manual_instructions():
    """Print instructions for manual table creation"""
    print("\n" + "=" * 50)
    print("📋 MANUAL SETUP REQUIRED")
    print("=" * 50)
    print()
    print("The Supabase Python client cannot create tables directly.")
    print("Please follow these steps:")
    print()
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Run the following SQL:")
    print()
    print("--- COPY THE SQL BELOW ---")
    print()
    
    sql = """-- Mock Twitter Posts table
CREATE TABLE mock_twitter_posts (
    id BIGSERIAL PRIMARY KEY,
    text TEXT NOT NULL CHECK (length(text) > 0),
    image TEXT, -- base64 encoded image or URL
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_mock_twitter_posts_timestamp ON mock_twitter_posts(timestamp);
CREATE INDEX idx_mock_twitter_posts_created_at ON mock_twitter_posts(created_at);

-- RLS policies
ALTER TABLE mock_twitter_posts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for authenticated users" ON mock_twitter_posts
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for service role" ON mock_twitter_posts
    FOR ALL USING (auth.role() = 'service_role');"""
    
    print(sql)
    print()
    print("--- END SQL ---")
    print()
    print("4. Click 'Run' to execute")
    print("5. Start your Mock Twitter server")
    print()
    print("✨ After setup, your posts will be saved to both:")
    print("   • Supabase (primary storage)")
    print("   • Local JSON file (backup)")

def main():
    """Main setup process"""
    success = create_mock_twitter_table()
    
    if success:
        print("\n🎉 Setup check completed!")
        print("\n🔄 Next steps:")
        print("   1. If table creation was needed, run the SQL in Supabase dashboard")
        print("   2. Start your Mock Twitter server: python server.py")
        print("   3. Use the interface - posts will be saved to both stores!")
    else:
        print("\n❌ Setup failed - please check the errors above")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 