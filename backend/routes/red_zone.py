"""
Red Zone trigger routes for Crisis-MMD backend.
Handles emergency Red Zone activation and user calling coordination.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import httpx
import logging
from datetime import datetime

from models import RedZoneTriggerRequest, RedZoneTriggerResponse
from database import db_service
from config import settings

router = APIRouter(prefix="/red-zone", tags=["red-zone"])
logger = logging.getLogger(__name__)

# Agent configuration - TODO: Move to config
AGENT_URL = "http://localhost:5001/trigger-calls"  # Default agent URL
AGENT_TIMEOUT = 30.0

@router.post("/trigger", response_model=RedZoneTriggerResponse)
async def trigger_red_zone(request: RedZoneTriggerRequest):
    """
    Trigger Red Zone emergency calling for a specific city.
    
    This endpoint:
    1. Gets all active users in the specified city
    2. Sends user data and incident info to the multi-modal calling agent
    3. Returns status and affected user count
    """
    try:
        logger.info(f"🚨 Red Zone triggered for city: {request.city}")
        
        # Step 1: Get all active users in the city
        users = await db_service.get_users_by_city(request.city)
        
        if not users:
            logger.warning(f"No active users found in city: {request.city}")
            return RedZoneTriggerResponse(
                success=True,
                message=f"Red Zone triggered but no active users found in {request.city}",
                affected_users_count=0,
                city=request.city,
                agent_response=None
            )
        
        logger.info(f"Found {len(users)} active users in {request.city}")
        
        # Step 2: Prepare data for the calling agent
        agent_payload = {
            "city": request.city,
            "incident_data": request.incident_data,
            "users": users,
            "triggered_at": datetime.utcnow().isoformat(),
            "total_users": len(users)
        }
        
        # Step 3: Send data to the multi-modal calling agent
        agent_response = await send_to_calling_agent(agent_payload)
        
        # Step 4: Return success response
        return RedZoneTriggerResponse(
            success=True,
            message=f"Red Zone triggered successfully for {request.city}. Calling {len(users)} users.",
            affected_users_count=len(users),
            city=request.city,
            agent_response=agent_response
        )
        
    except Exception as e:
        logger.error(f"Failed to trigger Red Zone for {request.city}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger Red Zone: {str(e)}"
        )

async def send_to_calling_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send user data and incident information to the multi-modal calling agent.
    
    Args:
        payload: Data to send to agent including users, city, and incident info
        
    Returns:
        Response from the calling agent
    """
    try:
        logger.info(f"Sending data to calling agent at {AGENT_URL}")
        
        async with httpx.AsyncClient(timeout=AGENT_TIMEOUT) as client:
            response = await client.post(
                AGENT_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                agent_response = response.json()
                logger.info(f"Agent responded successfully: {agent_response}")
                return agent_response
            else:
                logger.error(f"Agent returned error status {response.status_code}: {response.text}")
                return {
                    "error": f"Agent returned status {response.status_code}",
                    "details": response.text
                }
                
    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to calling agent at {AGENT_URL}")
        return {
            "error": "Agent timeout",
            "details": f"No response from agent within {AGENT_TIMEOUT} seconds"
        }
    except httpx.ConnectError:
        logger.error(f"Failed to connect to calling agent at {AGENT_URL}")
        return {
            "error": "Agent connection failed", 
            "details": f"Could not connect to agent at {AGENT_URL}"
        }
    except Exception as e:
        logger.error(f"Unexpected error sending to agent: {e}")
        return {
            "error": "Unexpected agent error",
            "details": str(e)
        } 