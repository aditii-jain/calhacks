#!/usr/bin/env python3
"""
Simple test script for the Crisis Classification API
"""

import json
import requests
import time

def test_api(base_url="http://localhost:3000"):
    """
    Test the crisis classification API with sample tweets
    
    Args:
        base_url (str): Base URL of the API (default: local dev server)
    """
    api_endpoint = f"{base_url}/api/classify_crisis"
    
    # Load test data
    try:
        with open('test_tweets.json', 'r') as f:
            test_tweets = json.load(f)
    except FileNotFoundError:
        print("❌ test_tweets.json not found in current directory")
        return
    except json.JSONDecodeError:
        print("❌ Invalid JSON in test_tweets.json")
        return
    
    print(f"🧪 Testing Crisis Classification API at: {api_endpoint}")
    print(f"📝 Found {len(test_tweets)} test tweets\n")
    
    for i, tweet_data in enumerate(test_tweets, 1):
        print(f"🔍 Test {i}/{len(test_tweets)}")
        print(f"Tweet: {tweet_data['tweet_text'][:60]}...")
        print(f"Image: {tweet_data['image_url']}")
        
        try:
            # Make API request
            response = requests.post(
                api_endpoint,
                json=tweet_data,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"   Disaster Type: {result.get('disaster_type')}")
                print(f"   Informative: {result.get('informativeness')}")
                print(f"   Categories: {', '.join(result.get('humanitarian_categories', []))}")
                print(f"   Location: {result.get('location')}")
                print(f"   Damage: {result.get('damage_severity')}")
                print(f"   Seriousness: {result.get('seriousness_score')}")
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is the server running?")
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
        
        # Small delay between requests
        if i < len(test_tweets):
            time.sleep(1)
    
    print("🏁 Testing completed!")

if __name__ == "__main__":
    import sys
    
    # Allow custom URL as command line argument
    url = sys.argv[1] if len(sys.argv) > 1 else "https://calhack4-lv6tbxp1y-suchis-projects-82d270e7.vercel.app"
    test_api(url)