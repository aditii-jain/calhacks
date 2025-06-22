"""Push Classification to Database API route - Stores crisis classification data in Supabase"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging
from database import get_supabase_client

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

def ensure_table_exists():
    """Ensure the crisis_tweets_classification table exists"""
    supabase = get_supabase_client()
    table_name = "crisis_tweets_classification"
    
    ddl = f'''
    create table if not exists {table_name} (
        id serial primary key,
        disaster_type text,
        informativeness text,
        humanitarian_categories jsonb,
        location text,
        damage_severity text,
        seriousness_score float8,
        tweet_text text unique,
        image_url text,
        timestamp text
    );
    '''
    try:
        # Try to execute SQL via RPC function if available
        supabase.postgrest.rpc("execute_sql", {"sql": ddl}).execute()
        logger.info("Table creation SQL executed via RPC")
    except Exception as e:
        # Ignore if already exists or if function not available
        logger.warning(f"Could not execute table creation SQL: {e}")
        pass

def push_classification_to_db(data: Dict[str, Any]) -> bool:
    """
    Push classification data to the database
    
    Returns:
        bool: True if inserted, False if tweet already exists
    """
    ensure_table_exists()
    supabase = get_supabase_client()
    table_name = "crisis_tweets_classification"
    
    try:
        # Check if tweet_text exists
        tweet_text = data.get("tweet_text", "")
        if tweet_text:
            existing = supabase.table(table_name).select("id").eq("tweet_text", tweet_text).execute()
            if existing.data:
                logger.info(f"Tweet already exists in database: {tweet_text[:50]}...")
                return False
        
        # Prepare insert data
        insert_data = {
            k: data.get(k) for k in [
                "disaster_type", "informativeness", "humanitarian_categories", "location",
                "damage_severity", "seriousness_score", "tweet_text", "image_url", "timestamp"
            ] if data.get(k) is not None
        }
        
        # Insert the data
        result = supabase.table(table_name).insert(insert_data).execute()
        logger.info(f"Successfully inserted classification data: {result.data}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to insert classification data: {e}")
        raise

@router.post("/push-classification-db")
async def push_classification_db(data: Dict[str, Any]):
    """
    Store crisis classification data in the database
    
    Expected data structure:
    {
        "disaster_type": "string",
        "informativeness": "string",
        "humanitarian_categories": ["list"],
        "location": "string",
        "damage_severity": "string", 
        "seriousness_score": 0.0,
        "tweet_text": "string",
        "image_url": "string",
        "timestamp": "string" (optional)
    }
    """
    
    try:
        # Validate required fields
        required_fields = ["disaster_type", "informativeness", "location", "tweet_text"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Push to database
        inserted = push_classification_to_db(data)
        
        logger.info(f"Classification data processing complete. Inserted: {inserted}")
        
        return {
            "inserted": inserted,
            "message": "Data inserted successfully" if inserted else "Tweet already exists in database"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to push classification to database: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")

@router.get("/push-classification-db/health")
async def push_classification_db_health():
    """Health check for push classification database endpoint"""
    
    try:
        # Test database connection
        supabase = get_supabase_client()
        result = supabase.table("crisis_tweets_classification").select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "service": "push_classification_db",
            "database_connected": True,
            "table_accessible": True,
            "supported_fields": [
                "disaster_type", "informativeness", "humanitarian_categories", 
                "location", "damage_severity", "seriousness_score", 
                "tweet_text", "image_url", "timestamp"
            ]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "push_classification_db", 
            "database_connected": False,
            "error": str(e)
        } 