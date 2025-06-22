"""Test script to populate crisis_location_aggregate table with sample data"""

import os
from supabase import create_client, Client
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample crisis data for testing
SAMPLE_CRISIS_DATA = [
    {
        "location": "Downtown Los Angeles",
        "disaster_type": "wildfire",
        "aggregate_score": 85.2,
        "tweet_count": 1247
    },
    {
        "location": "Santa Monica",
        "disaster_type": "wildfire",
        "aggregate_score": 72.8,
        "tweet_count": 892
    },
    {
        "location": "Beverly Hills",
        "disaster_type": "wildfire",
        "aggregate_score": 67.4,
        "tweet_count": 634
    },
    {
        "location": "San Francisco Financial District",
        "disaster_type": "earthquake",
        "aggregate_score": 78.9,
        "tweet_count": 1056
    },
    {
        "location": "Oakland",
        "disaster_type": "earthquake",
        "aggregate_score": 65.1,
        "tweet_count": 743
    },
    {
        "location": "San Jose",
        "disaster_type": "earthquake",
        "aggregate_score": 58.3,
        "tweet_count": 521
    },
    {
        "location": "Miami Beach",
        "disaster_type": "hurricane",
        "aggregate_score": 91.7,
        "tweet_count": 1583
    },
    {
        "location": "Fort Lauderdale",
        "disaster_type": "hurricane",
        "aggregate_score": 88.4,
        "tweet_count": 1342
    },
    {
        "location": "Key West",
        "disaster_type": "hurricane",
        "aggregate_score": 82.1,
        "tweet_count": 967
    },
    {
        "location": "Houston Heights",
        "disaster_type": "flood",
        "aggregate_score": 75.6,
        "tweet_count": 1124
    },
    {
        "location": "New Orleans French Quarter",
        "disaster_type": "flood",
        "aggregate_score": 69.2,
        "tweet_count": 834
    },
    {
        "location": "Baton Rouge",
        "disaster_type": "flood",
        "aggregate_score": 61.8,
        "tweet_count": 612
    },
    {
        "location": "Phoenix Scottsdale",
        "disaster_type": "wildfire",
        "aggregate_score": 54.7,
        "tweet_count": 456
    },
    {
        "location": "Tucson",
        "disaster_type": "wildfire",
        "aggregate_score": 48.3,
        "tweet_count": 327
    },
    {
        "location": "Seattle Capitol Hill",
        "disaster_type": "earthquake",
        "aggregate_score": 42.9,
        "tweet_count": 289
    },
    {
        "location": "Portland Downtown",
        "disaster_type": "wildfire",
        "aggregate_score": 39.6,
        "tweet_count": 234
    },
    {
        "location": "Denver LoDo",
        "disaster_type": "wildfire",
        "aggregate_score": 35.2,
        "tweet_count": 198
    },
    {
        "location": "Atlanta Midtown",
        "disaster_type": "hurricane",
        "aggregate_score": 41.8,
        "tweet_count": 312
    },
    {
        "location": "Nashville Music Row",
        "disaster_type": "flood",
        "aggregate_score": 33.7,
        "tweet_count": 187
    },
    {
        "location": "Austin Downtown",
        "disaster_type": "flood",
        "aggregate_score": 29.4,
        "tweet_count": 156
    }
]

def initialize_supabase():
    """Initialize Supabase client"""
    if not settings.supabase_url or not settings.supabase_service_key:
        raise ValueError("Supabase credentials not configured")
    
    client = create_client(
        settings.supabase_url, 
        settings.supabase_service_key
    )
    
    logger.info("Supabase client initialized")
    return client

def clear_existing_data(client: Client):
    """Clear existing crisis location data"""
    try:
        response = client.table("crisis_location_aggregate").delete().neq("id", 0).execute()
        logger.info(f"Cleared existing crisis data")
        return True
    except Exception as e:
        logger.error(f"Error clearing existing data: {e}")
        return False

def insert_sample_data(client: Client):
    """Insert sample crisis data"""
    try:
        response = client.table("crisis_location_aggregate").insert(SAMPLE_CRISIS_DATA).execute()
        
        if response.data:
            logger.info(f"Successfully inserted {len(response.data)} crisis location records")
            return len(response.data)
        else:
            logger.error("No data was inserted")
            return 0
            
    except Exception as e:
        logger.error(f"Error inserting sample data: {e}")
        raise

def verify_data(client: Client):
    """Verify the inserted data"""
    try:
        response = client.table("crisis_location_aggregate").select("*").execute()
        
        if response.data:
            logger.info(f"Verification: Found {len(response.data)} records in crisis_location_aggregate")
            
            # Show summary by disaster type
            disaster_counts = {}
            for record in response.data:
                disaster_type = record.get("disaster_type", "unknown")
                disaster_counts[disaster_type] = disaster_counts.get(disaster_type, 0) + 1
            
            logger.info("Crisis data by disaster type:")
            for disaster_type, count in disaster_counts.items():
                logger.info(f"  {disaster_type}: {count} locations")
            
            # Show top 5 highest scores
            sorted_data = sorted(response.data, key=lambda x: x.get("aggregate_score", 0), reverse=True)
            logger.info("Top 5 highest risk locations:")
            for i, record in enumerate(sorted_data[:5], 1):
                logger.info(f"  {i}. {record['location']} - {record['disaster_type']} (Score: {record['aggregate_score']})")
            
            return True
        else:
            logger.error("No data found after insertion")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying data: {e}")
        return False

def main():
    """Main function to populate crisis data"""
    
    logger.info("🚨 Crisis Location Data Population Script")
    logger.info("=" * 50)
    
    try:
        # Initialize Supabase
        client = initialize_supabase()
        
        # Ask user if they want to clear existing data
        while True:
            clear_choice = input("\nDo you want to clear existing crisis data first? (y/n): ").strip().lower()
            if clear_choice in ['y', 'yes']:
                logger.info("Clearing existing data...")
                clear_existing_data(client)
                break
            elif clear_choice in ['n', 'no']:
                logger.info("Keeping existing data...")
                break
            else:
                print("Please enter 'y' or 'n'")
        
        # Insert sample data
        logger.info(f"Inserting {len(SAMPLE_CRISIS_DATA)} sample crisis location records...")
        inserted_count = insert_sample_data(client)
        
        if inserted_count > 0:
            logger.info(f"✅ Successfully populated crisis_location_aggregate table")
            
            # Verify the data
            logger.info("Verifying inserted data...")
            verify_data(client)
            
            logger.info("\n🎯 Next steps:")
            logger.info("1. Start your backend server: uvicorn main:app --reload")
            logger.info("2. Start your frontend: npm run dev")
            logger.info("3. Visit http://localhost:3000/dashboard to see the heat map")
            logger.info("4. The crisis map will show real data from your Supabase table!")
            
        else:
            logger.error("❌ Failed to populate data")
            
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        raise

if __name__ == "__main__":
    main() 