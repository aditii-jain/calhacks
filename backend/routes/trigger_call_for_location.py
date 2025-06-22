"""Trigger Emergency Calls for Location API route - Triggers emergency calls for users in crisis areas"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import logging
from database import get_supabase_client
import sys
import os

# Add voice_agent module to path  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logger = logging.getLogger(__name__)

# Import the trigger call function
try:
    from voice_agent.trigger_call import trigger_emergency_call
    logger.info("Voice agent imported successfully")
except ImportError as e:
    logger.warning(f"Voice agent not available: {e}")
    trigger_emergency_call = None

router = APIRouter()

def trigger_call_for_location(location: str, disaster_type: str, timeout_minutes: int = 10) -> Dict[str, Any]:
    """
    Trigger emergency calls for all users in the specified location
    
    Args:
        location: Location string to match against user addresses
        disaster_type: Type of disaster for the emergency message
        timeout_minutes: Call timeout in minutes
        
    Returns:
        Dict containing list of called users and count
    """
    logger.info(f"Triggering calls for location='{location}', disaster_type='{disaster_type}'")
    
    supabase = get_supabase_client()
    
    try:
        # Query all users from the database
        users_result = supabase.table("active_users").select("phone_number, location").execute()
        logger.info(f"Found {len(users_result.data)} total users in database")
        
        if not users_result.data:
            logger.warning("No users found in database")
            return {"status": "no_users_found", "called_users": [], "count": 0}
        
        called_users = []
        
        for user in users_result.data:
            loc = user.get("location", {})
            
            # Handle different location formats
            if isinstance(loc, dict):
                address = loc.get("address", "")
            elif isinstance(loc, str):
                address = loc
            else:
                address = ""
            
            phone_number = user.get("phone_number", "")
            
            logger.debug(f"Checking user: address='{address}', phone_number='{phone_number}'")
            
            # Check if user's address matches the crisis location
            if address and phone_number and address.strip().lower() == location.strip().lower():
                logger.info(f"MATCH: Triggering emergency call for {phone_number} at {address}")
                
                # Check if trigger_emergency_call is available and VAPI API key is set
                vapi_api_key = os.getenv("VAPI_API_KEY")
                if trigger_emergency_call is None or not vapi_api_key:
                    logger.warning(f"Voice agent not available - trigger_emergency_call: {trigger_emergency_call is not None}, VAPI_API_KEY: {bool(vapi_api_key)}")
                    result = {
                        "status": "simulated", 
                        "message": f"Voice agent not available - Missing: {'VAPI_API_KEY' if not vapi_api_key else 'voice agent module'}",
                        "phone_number": phone_number,
                        "location": address,
                        "disaster_type": disaster_type,
                        "would_call": True
                    }
                else:
                    try:
                        # Call the emergency trigger function
                        result = trigger_emergency_call(
                            phone_number=phone_number,
                            location=address,
                            natural_disaster=disaster_type,
                            timeout_minutes=timeout_minutes
                        )
                        
                        # Check if the call was successful
                        if result.get("status") == "success" and not result.get("error"):
                            logger.info(f"Emergency call triggered successfully for {phone_number}")
                        else:
                            logger.error(f"Emergency call failed for {phone_number}: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        logger.error(f"Failed to trigger emergency call for {phone_number}: {e}")
                        result = {
                            "status": "error",
                            "call_id": None,
                            "send_directions": False,
                            "contact_emergency_contacts": False,
                            "google_maps_pin": None,
                            "error": str(e)
                        }
                
                called_users.append({
                    "phone_number": phone_number,
                    "address": address,
                    "result": result
                })
            else:
                logger.debug(f"SKIP: No match for user {phone_number} at {address}")
        
        logger.info(f"Emergency call process complete. Called {len(called_users)} users")
        
        return {
            "called_users": called_users,
            "count": len(called_users),
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger calls for location: {e}")
        raise

@router.post("/trigger-call-for-location")
async def trigger_call_for_location_endpoint(data: Dict[str, Any]):
    """
    Trigger emergency calls for all users in the affected location
    
    Expected data structure:
    {
        "location": "string",
        "disaster_type": "string",
        "timeout_minutes": 10 (optional)
    }
    
    Returns:
    {
        "called_users": [
            {
                "phone_number": "string",
                "address": "string", 
                "result": {...}
            }
        ],
        "count": 0,
        "status": "string"
    }
    """
    
    try:
        # Validate required fields
        location = data.get("location")
        disaster_type = data.get("disaster_type") 
        timeout_minutes = data.get("timeout_minutes", 10)
        
        if not location:
            raise HTTPException(status_code=400, detail="Missing required field: location")
            
        if not disaster_type:
            raise HTTPException(status_code=400, detail="Missing required field: disaster_type")
        
        # Validate timeout
        try:
            timeout_minutes = int(timeout_minutes)
            if timeout_minutes <= 0:
                timeout_minutes = 10
        except (ValueError, TypeError):
            timeout_minutes = 10
        
        logger.info(f"Processing emergency call request for {location}")
        
        # Trigger the calls
        result = trigger_call_for_location(location, disaster_type, timeout_minutes)
        
        logger.info(f"Emergency call request completed: {result.get('count', 0)} users called")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process emergency call request: {e}")
        raise HTTPException(status_code=500, detail=f"Emergency call processing failed: {str(e)}")

@router.get("/trigger-call-for-location/health")
async def trigger_call_for_location_health():
    """Health check for trigger call for location endpoint"""
    
    try:
        # Test database connection
        supabase = get_supabase_client()
        result = supabase.table("active_users").select("id").limit(1).execute()
        
        # Check if voice agent is available
        voice_agent_available = trigger_emergency_call is not None
        vapi_api_key_set = bool(os.getenv("VAPI_API_KEY"))
        
        return {
            "status": "healthy",
            "service": "trigger_call_for_location",
            "database_connected": True,
            "users_table_accessible": True,
            "voice_agent_module_available": voice_agent_available,
            "vapi_api_key_configured": vapi_api_key_set,
            "voice_calls_enabled": voice_agent_available and vapi_api_key_set,
            "assistant_id": "d97df5ae-d4b9-4644-9836-e22a19e0fbea",
            "phone_number_id": "4107aab6-6685-4a40-9344-586b9490b711",
            "supported_fields": ["location", "disaster_type", "timeout_minutes"],
            "location_matching": "exact string match (case insensitive)"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "trigger_call_for_location",
            "database_connected": False,
            "error": str(e)
        } 