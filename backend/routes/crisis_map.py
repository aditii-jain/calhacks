"""Crisis Map API routes - Fetch crisis location aggregate data for heat map visualization"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime

from config import settings
from supabase import create_client, Client

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Supabase client
supabase_client: Optional[Client] = None

def get_supabase_client():
    """Get or initialize Supabase client"""
    global supabase_client
    
    if not supabase_client:
        if not settings.supabase_url or not settings.supabase_service_key:
            raise HTTPException(
                status_code=500, 
                detail="Supabase credentials not configured"
            )
        
        try:
            supabase_client = create_client(
                settings.supabase_url, 
                settings.supabase_service_key
            )
            logger.info("Supabase client initialized for crisis map")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Database connection failed: {str(e)}"
            )
    
    return supabase_client

@router.get("/crisis-map/data")
async def get_crisis_map_data(
    min_score: Optional[float] = Query(None, description="Minimum aggregate score filter"),
    disaster_type: Optional[str] = Query(None, description="Filter by disaster type"),
    limit: Optional[int] = Query(100, description="Maximum number of locations to return")
):
    """
    Get crisis location aggregate data for heat map visualization
    
    Returns crisis data with locations, disaster types, scores, and tweet counts
    """
    
    client = get_supabase_client()
    
    try:
        # Build query
        query = client.table("crisis_location_aggregate").select("*")
        
        # Apply filters
        if min_score is not None:
            query = query.gte("aggregate_score", min_score)
        
        if disaster_type:
            query = query.eq("disaster_type", disaster_type)
        
        # Order by score (highest first) and limit results
        query = query.order("aggregate_score", desc=True).limit(limit)
        
        response = query.execute()
        
        # Process data for frontend
        crisis_data = []
        for record in response.data:
            # Convert score from 0-1 range to 0-100 range if needed
            raw_score = record["aggregate_score"]
            normalized_score = raw_score * 100 if raw_score and raw_score <= 1 else raw_score
            
            crisis_point = {
                "id": record["id"],
                "location": record["location"],
                "disaster_type": record["disaster_type"],
                "aggregate_score": normalized_score,
                "raw_score": raw_score,  # Keep original for reference
                "tweet_count": record["tweet_count"],
                "severity": _get_severity_level(normalized_score),
                "color": _get_heat_map_color(normalized_score)
            }
            crisis_data.append(crisis_point)
        
        return {
            "status": "success",
            "data": crisis_data,
            "total_locations": len(crisis_data),
            "filters": {
                "min_score": min_score,
                "disaster_type": disaster_type,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch crisis map data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch crisis data: {str(e)}"
        )

@router.get("/crisis-map/summary")
async def get_crisis_summary():
    """
    Get summary statistics for the crisis map
    """
    
    client = get_supabase_client()
    
    try:
        # Get all crisis data for analysis
        response = client.table("crisis_location_aggregate").select("*").execute()
        
        if not response.data:
            return {
                "status": "success",
                "summary": {
                    "total_locations": 0,
                    "disaster_types": [],
                    "score_ranges": {},
                    "total_tweets": 0
                }
            }
        
        # Calculate summary statistics
        data = response.data
        total_locations = len(data)
        total_tweets = sum(record["tweet_count"] or 0 for record in data)
        
        # Get unique disaster types
        disaster_types = list(set(record["disaster_type"] for record in data if record["disaster_type"]))
        
        # Score distribution
        scores = [record["aggregate_score"] for record in data if record["aggregate_score"]]
        score_ranges = {
            "extreme": len([s for s in scores if s >= 80]),
            "high": len([s for s in scores if 60 <= s < 80]),
            "moderate": len([s for s in scores if 40 <= s < 60]),
            "low": len([s for s in scores if s < 40])
        }
        
        # Top affected locations
        top_locations = sorted(
            data, 
            key=lambda x: x["aggregate_score"] or 0, 
            reverse=True
        )[:5]
        
        return {
            "status": "success",
            "summary": {
                "total_locations": total_locations,
                "disaster_types": disaster_types,
                "score_ranges": score_ranges,
                "total_tweets": total_tweets,
                "top_affected_locations": [
                    {
                        "location": loc["location"],
                        "disaster_type": loc["disaster_type"],
                        "score": loc["aggregate_score"],
                        "tweet_count": loc["tweet_count"]
                    }
                    for loc in top_locations
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get crisis summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get crisis summary: {str(e)}"
        )

@router.get("/crisis-map/disaster-types")
async def get_disaster_types():
    """
    Get list of all disaster types in the database
    """
    
    client = get_supabase_client()
    
    try:
        response = client.table("crisis_location_aggregate")\
            .select("disaster_type")\
            .execute()
        
        # Get unique disaster types
        disaster_types = list(set(
            record["disaster_type"] 
            for record in response.data 
            if record["disaster_type"]
        ))
        
        return {
            "status": "success",
            "disaster_types": sorted(disaster_types)
        }
        
    except Exception as e:
        logger.error(f"Failed to get disaster types: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get disaster types: {str(e)}"
        )

def _get_severity_level(score: float) -> str:
    """Convert aggregate score to severity level"""
    if score is None:
        return "unknown"
    
    # Updated thresholds: above 60 is high, below 60 is low
    if score >= 60:
        return "high"
    else:
        return "low"

def _get_heat_map_color(score: float) -> str:
    """Get heat map color based on aggregate score"""
    if score is None:
        return "#gray-400"
    
    # Updated colors: above 60 is red (high), below 60 is yellow (low)
    if score >= 60:
        return "#ef4444"  # red-500 - high
    else:
        return "#eab308"  # yellow-500 - low risk

@router.get("/crisis-map/health")
async def crisis_map_health():
    """Health check for crisis map API with detailed debugging"""
    
    try:
        logger.info("🔍 Starting crisis map health check...")
        
        # Check Supabase credentials
        logger.info(f"Supabase URL configured: {bool(settings.supabase_url)}")
        logger.info(f"Supabase Service Key configured: {bool(settings.supabase_service_key)}")
        
        client = get_supabase_client()
        logger.info("✅ Supabase client created successfully")
        
        # Test connection with table query
        response = client.table("crisis_location_aggregate")\
            .select("*")\
            .limit(5)\
            .execute()
        
        logger.info(f"📊 Health check query returned {len(response.data)} rows")
        logger.info(f"🔍 Sample data from health check:")
        for i, record in enumerate(response.data[:3]):
            logger.info(f"  Row {i+1}: {record}")
        
        # Get table count
        count_response = client.table("crisis_location_aggregate").select("id", count="exact").execute()
        total_count = count_response.count if hasattr(count_response, 'count') else len(response.data)
        
        return {
            "status": "healthy",
            "database_connected": True,
            "table_accessible": True,
            "total_rows": total_count,
            "sample_data": response.data[:3],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Crisis map health check failed: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {
            "status": "unhealthy",
            "database_connected": False,
            "table_accessible": False,
            "error": str(e),
            "error_type": str(type(e)),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/crisis-map/geocode/{location}")
async def geocode_location(location: str):
    """
    Geocode a location to get lat/lng coordinates and convert to map position
    """
    
    # Built-in coordinate database for common US locations
    US_LOCATION_COORDS = {
        # West Coast
        'Los Angeles': { 'lat': 34.0522, 'lng': -118.2437, 'x': 15, 'y': 70 },
        'San Francisco': { 'lat': 37.7749, 'lng': -122.4194, 'x': 8, 'y': 50 },
        'California': { 'lat': 36.7783, 'lng': -119.4179, 'x': 12, 'y': 60 },
        'Sacramento, California': { 'lat': 38.5816, 'lng': -121.4944, 'x': 10, 'y': 55 },
        'Santa Rosa': { 'lat': 38.4404, 'lng': -122.7144, 'x': 8, 'y': 52 },
        'Portland': { 'lat': 45.5152, 'lng': -122.6784, 'x': 12, 'y': 35 },
        
        # Texas
        'Houston': { 'lat': 29.7604, 'lng': -95.3698, 'x': 45, 'y': 80 },
        'Houston, Texas': { 'lat': 29.7604, 'lng': -95.3698, 'x': 45, 'y': 80 },
        'Houston, TX': { 'lat': 29.7604, 'lng': -95.3698, 'x': 45, 'y': 80 },
        'Dallas': { 'lat': 32.7767, 'lng': -96.7970, 'x': 45, 'y': 75 },
        'San Antonio': { 'lat': 29.4241, 'lng': -98.4936, 'x': 42, 'y': 82 },
        'Austin': { 'lat': 30.2672, 'lng': -97.7431, 'x': 43, 'y': 78 },
        
        # Florida
        'Miami': { 'lat': 25.7617, 'lng': -80.1918, 'x': 75, 'y': 90 },
        'Miami, Florida': { 'lat': 25.7617, 'lng': -80.1918, 'x': 75, 'y': 90 },
        'Tampa': { 'lat': 27.9506, 'lng': -82.4572, 'x': 72, 'y': 85 },
        'Orlando': { 'lat': 28.5383, 'lng': -81.3792, 'x': 73, 'y': 83 },
        'Jacksonville': { 'lat': 30.3322, 'lng': -81.6557, 'x': 73, 'y': 78 },
        
        # East Coast
        'New York': { 'lat': 40.7128, 'lng': -74.0060, 'x': 68, 'y': 45 },
        'New York City': { 'lat': 40.7128, 'lng': -74.0060, 'x': 68, 'y': 45 },
        'Boston': { 'lat': 42.3601, 'lng': -71.0589, 'x': 70, 'y': 40 },
        'Philadelphia': { 'lat': 39.9526, 'lng': -75.1652, 'x': 68, 'y': 48 },
        'Washington DC': { 'lat': 38.9072, 'lng': -77.0369, 'x': 69, 'y': 55 },
        'Atlanta': { 'lat': 33.7490, 'lng': -84.3880, 'x': 72, 'y': 70 },
        'Charleston, WV': { 'lat': 38.3498, 'lng': -81.6326, 'x': 70, 'y': 58 },
        
        # Midwest
        'Chicago': { 'lat': 41.8781, 'lng': -87.6298, 'x': 60, 'y': 50 },
        'Detroit': { 'lat': 42.3314, 'lng': -83.0458, 'x': 62, 'y': 45 },
        
        # Caribbean/Territories
        'San Juan, Puerto Rico': { 'lat': 18.4655, 'lng': -66.1057, 'x': 80, 'y': 85 },
        'Charlotte Amalie, U.S. Virgin Islands': { 'lat': 18.3419, 'lng': -64.9307, 'x': 82, 'y': 88 },
        'St. Martin': { 'lat': 18.0708, 'lng': -63.0501, 'x': 85, 'y': 85 },
        'Roseau, Dominica': { 'lat': 15.2976, 'lng': -61.3900, 'x': 85, 'y': 90 },
    }
    
    try:
        # Decode URL-encoded location
        import urllib.parse
        decoded_location = urllib.parse.unquote(location)
        
        # Check exact match first
        if decoded_location in US_LOCATION_COORDS:
            coords = US_LOCATION_COORDS[decoded_location]
            return {
                "status": "success",
                "location": decoded_location,
                "coordinates": coords,
                "source": "built-in_database"
            }
        
        # Check partial matches
        for key, coords in US_LOCATION_COORDS.items():
            if (decoded_location.lower() in key.lower() or 
                key.lower() in decoded_location.lower()):
                return {
                    "status": "success", 
                    "location": decoded_location,
                    "matched_key": key,
                    "coordinates": coords,
                    "source": "built-in_database_partial"
                }
        
        # Try external geocoding as fallback (with better error handling)
        try:
            import requests
            import time
            
            # Add delay to respect rate limits
            time.sleep(0.1)
            
            response = requests.get(
                f"https://nominatim.openstreetmap.org/search",
                params={
                    'format': 'json',
                    'q': decoded_location,
                    'limit': 1,
                    'countrycodes': 'us'
                },
                headers={
                    'User-Agent': 'CrisisMap/1.0 (emergency-response-app)',
                    'Accept': 'application/json'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lng = float(data[0]['lon'])
                    
                    # Convert to map coordinates
                    US_BOUNDS = {
                        'north': 49.3457868,
                        'south': 24.7433195,  
                        'west': -124.7844079,
                        'east': -66.9513812
                    }
                    
                    x = max(5, min(95, ((lng - US_BOUNDS['west']) / (US_BOUNDS['east'] - US_BOUNDS['west'])) * 100))
                    y = max(10, min(90, ((US_BOUNDS['north'] - lat) / (US_BOUNDS['north'] - US_BOUNDS['south'])) * 100))
                    
                    coords = {
                        'lat': lat,
                        'lng': lng, 
                        'x': x,
                        'y': y
                    }
                    
                    return {
                        "status": "success",
                        "location": decoded_location,
                        "coordinates": coords,
                        "source": "external_api"
                    }
                    
        except Exception as api_error:
            logger.warning(f"External geocoding API failed: {api_error}")
        
        # Ultimate fallback
        fallback_coords = {
            'lat': 39.8283,  # Center of US
            'lng': -98.5795,
            'x': 50, 
            'y': 60
        }
        
        return {
            "status": "success",
            "location": decoded_location,
            "coordinates": fallback_coords,
            "source": "fallback_center",
            "warning": "Location not found, using US center"
        }
        
    except Exception as e:
        logger.error(f"Geocoding failed for location {location}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Geocoding failed: {str(e)}"
        ) 