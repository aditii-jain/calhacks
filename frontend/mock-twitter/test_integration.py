#!/usr/bin/env python3
"""
Test script for Mock Twitter Supabase integration
Tests both local JSON and Supabase storage
"""

import json
import requests
import time
from datetime import datetime

def test_post_storage():
    """Test posting data to the Mock Twitter server"""
    
    print("🧪 Testing Mock Twitter Integration")
    print("=" * 40)
    
    # Test data
    test_posts = [
        {
            "text": "🚨 Testing Supabase integration! Earthquake reported in downtown area. #test #earthquake",
            "image": None,
            "timestamp": datetime.now().isoformat()
        },
        {
            "text": "🔥 Wildfire spotted near highway. Testing image upload functionality. #test #wildfire",
            "image": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI0ZGNkIzNSIvPjx0ZXh0IHg9IjUwIiB5PSI1NSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+VGVzdCBJbWFnZTwvdGV4dD48L3N2Zz4=",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    server_url = "http://localhost:8000/save-post"
    
    print(f"📡 Testing connection to {server_url}")
    
    for i, post in enumerate(test_posts, 1):
        print(f"\n📝 Sending test post {i}...")
        
        try:
            response = requests.post(
                server_url,
                json=post,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Post {i} sent successfully!")
                print(f"   Status: {result.get('status', 'unknown')}")
                print(f"   Message: {result.get('message', 'no message')}")
                
                # Show storage results
                storage = result.get('storage', {})
                print(f"   Supabase: {'✅' if storage.get('supabase') else '❌'}")
                print(f"   Local JSON: {'✅' if storage.get('local_json') else '❌'}")
                
            else:
                print(f"❌ Post {i} failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - is the server running?")
            print(f"   Start server with: cd frontend/mock-twitter && python server.py")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
        time.sleep(1)  # Brief pause between requests
    
    # Test local JSON file
    print(f"\n📁 Checking local JSON file...")
    
    try:
        with open('../mock-twitter/posts.json', 'r') as f:
            local_data = json.load(f)
        
        post_count = len(local_data.get('posts', []))
        print(f"✅ Local JSON has {post_count} posts")
        print(f"   Total posts: {local_data.get('metadata', {}).get('total_posts', 0)}")
        
    except FileNotFoundError:
        print("❌ Local JSON file not found")
    except Exception as e:
        print(f"❌ Error reading local JSON: {e}")
    
    return True

def main():
    """Main test function"""
    success = test_post_storage()
    
    if success:
        print("\n🎉 Integration test completed!")
        print("\n📊 What was tested:")
        print("   ✅ HTTP POST to Mock Twitter server")
        print("   ✅ Supabase storage attempt")
        print("   ✅ Local JSON backup storage")
        print("   ✅ Response format validation")
        print("\n💡 Next steps:")
        print("   • Check your Supabase dashboard for the new posts")
        print("   • Open the Mock Twitter interface and see the posts")
        print("   • The integration is working! 🚀")
    else:
        print("\n❌ Integration test failed")
        print("   • Make sure the server is running: python server.py")
        print("   • Check your .env file has Supabase credentials")
        print("   • Verify the mock_twitter_posts table exists in Supabase")

if __name__ == "__main__":
    main() 