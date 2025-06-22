"""Get Aggregate Crisis Data API route - Calculates and updates aggregate crisis scores by location"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import logging
from database import get_supabase_client

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

def calc_aggregate_score(data: Dict[str, Any]) -> float:
    """
    Calculate aggregate crisis score based on various factors
    
    Score components:
    - 50% seriousness score (0.0-1.0)
    - 20% informativeness (1.0 if informative, 0.0 if not)
    - 20% damage severity (severe=1.0, mild=0.5, little=0.1, cannot_assess=0.0)
    - 10% humanitarian categories count (max 9 categories, normalized)
    
    Returns:
        float: Aggregate score between 0.0 and 1.0
    """
    try:
        # Seriousness score (50% weight)
        seriousness = float(data.get("seriousness_score", 0))
        
        # Informativeness (20% weight)
        informativeness = 1.0 if data.get("informativeness") == "informative" else 0.0
        
        # Damage severity (20% weight)
        damage_map = {
            "severe_damage": 1.0,
            "mild_damage": 0.5,
            "little_or_no_damage": 0.1,
            "cannot_assess": 0.0
        }
        damage = damage_map.get(data.get("damage_severity", ""), 0.0)
        
        # Humanitarian categories (10% weight)
        hum_cats = data.get("humanitarian_categories", [])
        if isinstance(hum_cats, list):
            # Count non-'none' categories, max 9
            valid_cats = [c for c in hum_cats if c != 'none']
            hum_score = min(len(valid_cats), 9) / 9.0
        else:
            hum_score = 0.0
        
        # Calculate weighted score
        aggregate_score = (
            0.5 * seriousness +
            0.2 * informativeness +
            0.2 * damage +
            0.1 * hum_score
        )
        
        return round(aggregate_score, 4)
        
    except Exception as e:
        logger.error(f"Failed to calculate aggregate score: {e}")
        return 0.0

def upsert_aggregate(location: str, new_score: float, disaster_type: str) -> tuple[float, int, str]:
    """
    Update or insert aggregate data for a location
    
    Args:
        location: Location string
        new_score: New aggregate score to incorporate
        disaster_type: Type of disaster
        
    Returns:
        tuple: (running_average_score, total_tweet_count, disaster_type)
    """
    supabase = get_supabase_client()
    agg_table = "crisis_location_aggregate"
    
    try:
        # Get current aggregate data for this location
        result = supabase.table(agg_table).select("id, aggregate_score, tweet_count").eq("location", location).execute()
        
        if result.data:
            # Update existing record
            row = result.data[0]
            current_count = row.get("tweet_count", 1)
            current_score = row.get("aggregate_score", 0)
            
            # Calculate new running average
            new_count = current_count + 1
            running_avg = (current_score * current_count + new_score) / new_count
            
            # Update the record
            update_result = supabase.table(agg_table).update({
                "aggregate_score": running_avg,
                "tweet_count": new_count,
                "disaster_type": disaster_type  # Update to most recent disaster type
            }).eq("location", location).execute()
            
            logger.info(f"Updated aggregate for {location}: score={running_avg:.4f}, count={new_count}")
            return running_avg, new_count, disaster_type
            
        else:
            # Insert new record
            insert_result = supabase.table(agg_table).insert({
                "location": location,
                "disaster_type": disaster_type,
                "aggregate_score": new_score,
                "tweet_count": 1
            }).execute()
            
            logger.info(f"Created new aggregate for {location}: score={new_score:.4f}, count=1")
            return new_score, 1, disaster_type
            
    except Exception as e:
        logger.error(f"Failed to upsert aggregate data: {e}")
        raise

@router.post("/get-aggregate")
async def get_aggregate(data: Dict[str, Any]):
    """
    Calculate and update aggregate crisis data for a location
    
    Expected data structure:
    {
        "location": "string",
        "disaster_type": "string", 
        "seriousness_score": 0.0,
        "informativeness": "string",
        "damage_severity": "string",
        "humanitarian_categories": ["list"]
    }
    
    Returns:
    {
        "location": "string",
        "disaster_type": "string",
        "aggregate_score": 0.0,
        "tweet_count": 1
    }
    """
    
    try:
        # Validate required fields
        location = data.get("location")
        disaster_type = data.get("disaster_type")
        
        if not location:
            raise HTTPException(status_code=400, detail="Missing required field: location")
        
        if not disaster_type:
            logger.warning("No disaster_type provided, using 'unknown'")
            disaster_type = "unknown"
        
        # Calculate aggregate score for this data point
        agg_score = calc_aggregate_score(data)
        logger.info(f"Calculated aggregate score for {location}: {agg_score:.4f}")
        
        # Update aggregate data in database
        avg_score, tweet_count, final_disaster_type = upsert_aggregate(location, agg_score, disaster_type)
        
        result = {
            "location": location,
            "disaster_type": final_disaster_type,
            "aggregate_score": avg_score,
            "tweet_count": tweet_count
        }
        
        logger.info(f"Aggregate data updated successfully: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get/update aggregate data: {e}")
        raise HTTPException(status_code=500, detail=f"Aggregate calculation failed: {str(e)}")

@router.get("/get-aggregate/health")
async def get_aggregate_health():
    """Health check for get aggregate endpoint"""
    
    try:
        # Test database connection
        supabase = get_supabase_client()
        result = supabase.table("crisis_location_aggregate").select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "service": "get_aggregate",
            "database_connected": True,
            "table_accessible": True,
            "score_calculation": {
                "seriousness_weight": 0.5,
                "informativeness_weight": 0.2,
                "damage_severity_weight": 0.2,
                "humanitarian_categories_weight": 0.1
            },
            "supported_fields": [
                "location", "disaster_type", "seriousness_score", 
                "informativeness", "damage_severity", "humanitarian_categories"
            ]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "get_aggregate",
            "database_connected": False,
            "error": str(e)
        } 