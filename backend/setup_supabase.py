#!/usr/bin/env python3
"""Setup script for Supabase database schema deployment - Classified Data Schema"""

import os
import sys
from supabase import create_client
from config import settings

def read_schema_file():
    """Read the database schema SQL file"""
    schema_path = "database_schema.sql"
    
    if not os.path.exists(schema_path):
        print(f"❌ Schema file not found: {schema_path}")
        return None
    
    try:
        with open(schema_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading schema file: {e}")
        return None

def test_supabase_connection():
    """Test connection to Supabase"""
    print("🔍 Testing Supabase connection...")
    
    if not settings.supabase_url or not settings.supabase_service_key:
        print("❌ Supabase credentials not configured")
        print("   Please check your .env file has:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_KEY")
        return False
    
    print(f"   URL: {settings.supabase_url[:30]}...")
    print(f"   Service Key: {settings.supabase_service_key[:20]}...")
    
    try:
        client = create_client(settings.supabase_url, settings.supabase_service_key)
        print("✅ Supabase client created successfully")
        return client
        
    except Exception as e:
        print(f"❌ Supabase client creation failed: {e}")
        print("   Common issues:")
        print("   - Wrong SUPABASE_URL format (should start with https://)")
        print("   - Wrong SUPABASE_SERVICE_KEY (check your project settings)")
        print("   - Network connectivity issues")
        return False

def check_existing_tables(client):
    """Check if tables already exist"""
    print("\n🔍 Checking for existing tables...")
    
    try:
        # Try to query the classified_data table
        response = client.table('classified_data').select('id').limit(1).execute()
        print("⚠️  Tables already exist!")
        print("   Found existing 'classified_data' table")
        
        # Get count of existing records
        try:
            count_response = client.table('classified_data').select('id', count='exact').execute()
            record_count = count_response.count or 0
            
            if record_count > 0:
                print(f"   Existing records: {record_count}")
            else:
                print("   Tables exist but are empty")
        except:
            print("   Tables exist (count check failed)")
            
        return True
            
    except Exception as e:
        error_msg = str(e).lower()
        if "does not exist" in error_msg or "relation" in error_msg or "42p01" in error_msg:
            print("✅ No existing tables found - ready for schema deployment")
            return False
        else:
            print(f"⚠️  Could not check tables: {e}")
            print("   This might be due to permissions or the tables not existing yet")
            print("   Proceeding with schema deployment...")
            return False

def deploy_schema(client, schema_sql):
    """Deploy the database schema to Supabase"""
    print("\n🚀 Deploying database schema...")
    
    try:
        # Note: Supabase Python client doesn't support raw SQL execution
        # Users need to run this in the Supabase dashboard
        print("📋 MANUAL STEP REQUIRED:")
        print("   The Supabase Python client doesn't support raw SQL execution.")
        print("   Please follow these steps:")
        print("\n   1. Go to your Supabase dashboard")
        print("   2. Navigate to SQL Editor")
        print("   3. Copy and paste the contents of 'database_schema.sql'")
        print("   4. Click 'Run' to execute the schema")
        print("\n   The schema file contains:")
        print("   - classified_data table (stores all classified tweet data)")
        print("   - Enum types for classification labels")
        print("   - Indexes for performance")
        print("   - Views for common queries")
        print("   - Row Level Security policies")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema deployment failed: {e}")
        return False

def verify_schema_deployment(client):
    """Verify that the schema was deployed correctly"""
    print("\n🔍 Verifying schema deployment...")
    
    required_tables = ['classified_data']
    
    for table in required_tables:
        try:
            response = client.table(table).select('*').limit(1).execute()
            print(f"✅ Table '{table}' exists and is accessible")
        except Exception as e:
            print(f"❌ Table '{table}' not found or not accessible: {e}")
            return False
    
    # Test inserting a sample record with unique ID
    try:
        import time
        unique_id = int(time.time() * 1000) + 888888  # Generate unique test ID
        
        test_record = {
            "tweet_id": unique_id,
            "image_id": f"{unique_id}_1",
            "text_info": "informative",
            "text_info_conf": 0.85,
            "image_info": "not_informative",
            "image_info_conf": 0.65,
            "text_human": "other_relevant_information",
            "text_human_conf": 0.75,
            "image_human": "not_humanitarian",
            "image_human_conf": 0.55,
            "image_damage": "little_or_no_damage",
            "image_damage_conf": 0.45,
            "tweet_text": "Test tweet for schema verification - this will be deleted",
            "image_url": "https://example.com/test.jpg",
            "image_path": "data_image/test/test.jpg",
            "location": "Test Location"
        }
        
        response = client.table('classified_data').insert(test_record).execute()
        
        if response.data:
            # Clean up test record
            test_id = response.data[0]['id']
            client.table('classified_data').delete().eq('id', test_id).execute()
            print("✅ Schema verification successful - can insert and delete records")
            return True
        else:
            print("❌ Schema verification failed - could not insert test record")
            return False
            
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        print("   Common issues:")
        print("   - Enum values don't match (check informative_label, humanitarian_label, damage_label)")
        print("   - Missing required fields")
        print("   - Constraint violations")
        return False

def update_config_to_use_supabase():
    """Update configuration to use Supabase"""
    print("\n🔧 Updating configuration...")
    
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        return False
    
    try:
        # Read current .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add USE_SUPABASE setting
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('USE_SUPABASE='):
                lines[i] = 'USE_SUPABASE=true\n'
                updated = True
                break
        
        if not updated:
            lines.append('USE_SUPABASE=true\n')
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print("✅ Configuration updated to use Supabase")
        print("   Set USE_SUPABASE=true in .env file")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False

def main():
    """Main setup process"""
    print("🛠️  Crisis-MMD Supabase Setup - Classified Data Schema")
    print("=" * 60)
    
    # Step 1: Read schema file
    schema_sql = read_schema_file()
    if not schema_sql:
        return False
    
    # Step 2: Test connection
    client = test_supabase_connection()
    if not client:
        return False
    
    # Step 3: Check existing tables
    existing_tables = check_existing_tables(client)
    if existing_tables is None:
        return False
    
    if existing_tables:
        print("\n🤔 Tables already exist. What would you like to do?")
        print("   1. Continue with existing tables")
        print("   2. Exit (recommended if you have data)")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "2":
            print("✅ Exiting to preserve existing data")
            return True
        elif choice != "1":
            print("❌ Invalid choice")
            return False
    
    # Step 4: Deploy schema (manual step)
    if not existing_tables:
        deploy_success = deploy_schema(client, schema_sql)
        if not deploy_success:
            return False
        
        print("\n⏳ Waiting for you to deploy the schema...")
        input("Press Enter after you've run the schema in Supabase dashboard...")
    
    # Step 5: Verify deployment
    if not verify_schema_deployment(client):
        return False
    
    # Step 6: Update configuration
    if not update_config_to_use_supabase():
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Supabase setup completed successfully!")
    print("\n✅ What was accomplished:")
    print("   ✅ Supabase connection verified")
    print("   ✅ Database schema deployed (classified_data table)")
    print("   ✅ Schema verification passed")
    print("   ✅ Configuration updated to use Supabase")
    print("\n🔄 Next steps:")
    print("   1. Restart your FastAPI server")
    print("   2. Test the API endpoints")
    print("   3. Start storing classified data!")
    print("\n📊 Available views in your database:")
    print("   - informative_data: Records with informative classifications")
    print("   - humanitarian_data: Records with humanitarian classifications")
    print("   - damage_assessment_data: Records with damage assessments")
    print("   - high_confidence_text: High-confidence text classifications")
    print("   - high_confidence_image: High-confidence image classifications")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 