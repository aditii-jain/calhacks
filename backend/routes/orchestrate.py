"""Orchestrate API route - Handles crisis classification and alert triggering workflow"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import requests
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# API URLs (you can move these to config later)
CLASSIFY_API_URL = "https://calhack4.vercel.app/api/classify_crisis"
PUSH_DB_API_URL = "https://calhack4.vercel.app/api/push_classification_db"
GET_AGGREGATE_API_URL = "https://calhack4.vercel.app/api/get_aggregate"
TRIGGER_CALL_API_URL = "https://calhack4.vercel.app/api/trigger_call_for_location"

def trigger_crisis_alert(aggregate_data: Dict[str, Any]) -> bool:
    """
    Triggers emergency calls for all users in the affected location by calling the API endpoint.
    """
    location = aggregate_data.get("location")
    disaster_type = aggregate_data.get("disaster_type")
    
    if not location or not disaster_type:
        logger.warning(f"Missing location or disaster_type in aggregate data: {aggregate_data}")
        return False
        
    try:
        logger.info(f"Triggering crisis alert for {location} - {disaster_type}")
        resp = requests.post(
            TRIGGER_CALL_API_URL,
            json={"location": location, "disaster_type": disaster_type},
            timeout=30
        )
        
        if resp.status_code == 200:
            result = resp.json()
            call_count = result.get("count", 0)
            logger.info(f"Crisis alert triggered successfully - {call_count} calls initiated")
            return bool(result and call_count > 0)
        else:
            logger.error(f"Crisis alert API failed: {resp.status_code} - {resp.text}")
            return False
            
    except Exception as e:
        logger.error(f"Exception triggering crisis alert: {e}")
        return False

@router.post("/orchestrate")
async def orchestrate_crisis_workflow(request_data: Dict[str, Any]):
    """
    Orchestrates the complete crisis detection workflow:
    1. Classify crisis data
    2. Push to database
    3. Get aggregated data
    4. Trigger alerts if thresholds are met
    """
    
    try:
        logger.info("Starting crisis orchestration workflow")
        
        # Step 1: Forward to classifier API
        logger.info("Step 1: Classifying crisis data")
        try:
            classify_resp = requests.post(CLASSIFY_API_URL, json=request_data, timeout=60)
            if classify_resp.status_code != 200:
                raise HTTPException(
                    status_code=classify_resp.status_code,
                    detail=f"Classification API failed: {classify_resp.text}"
                )
            classification = classify_resp.json()
            logger.info(f"Classification successful: {classification}")
        except requests.RequestException as e:
            logger.error(f"Classification API request failed: {e}")
            raise HTTPException(status_code=500, detail=f"Classification API request failed: {str(e)}")

        # Step 2: Forward to push_classification_db API
        logger.info("Step 2: Pushing classification to database")
        try:
            db_resp = requests.post(PUSH_DB_API_URL, json=classification, timeout=30)
            if db_resp.status_code != 200:
                inserted = False
                db_result = {"error": db_resp.text}
                logger.warning(f"Database push failed: {db_resp.text}")
            else:
                db_result = db_resp.json()
                inserted = db_result.get("inserted", False)
                logger.info(f"Database push result: {db_result}")
        except requests.RequestException as e:
            logger.error(f"Database API request failed: {e}")
            inserted = False
            db_result = {"error": str(e)}

        # Step 3 & 4: Get aggregate data and trigger alerts if needed
        alert_triggered = False
        agg_result = None
        
        if inserted:
            logger.info("Step 3: Getting aggregate data")
            try:
                agg_resp = requests.post(GET_AGGREGATE_API_URL, json=classification, timeout=30)
                if agg_resp.status_code == 200:
                    agg_result = agg_resp.json()
                    logger.info(f"Aggregate data: {agg_result}")
                    
                    # Step 4: Check thresholds and trigger alert if needed
                    if "error" not in agg_result:
                        tweet_count = agg_result.get("tweet_count", 0)
                        aggregate_score = agg_result.get("aggregate_score", 0)
                        
                        logger.info(f"Checking alert thresholds - tweet_count: {tweet_count}, aggregate_score: {aggregate_score}")
                        
                        if tweet_count > 7 and aggregate_score > 0.75:
                            logger.info("Thresholds met - triggering crisis alert")
                            alert_triggered = trigger_crisis_alert(agg_result)
                            logger.info(f"Alert triggered result: {alert_triggered}")
                        else:
                            logger.info("Thresholds not met - no alert triggered")
                else:
                    agg_result = {"error": agg_resp.text}
                    logger.warning(f"Aggregate API failed: {agg_resp.text}")
                    
            except requests.RequestException as e:
                logger.error(f"Aggregate API request failed: {e}")
                agg_result = {"error": str(e)}

        # Return comprehensive result
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "classification": classification,
            "database": {
                "inserted": inserted,
                "result": db_result
            },
            "aggregate": agg_result,
            "alert": {
                "triggered": alert_triggered,
                "reason": "thresholds_met" if alert_triggered else "thresholds_not_met"
            }
        }
        
        logger.info(f"Orchestration completed successfully: {result}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in orchestration workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

@router.get("/orchestrate/health")
async def orchestrate_health():
    """Health check for orchestrate endpoint"""
    return {
        "status": "healthy",
        "service": "orchestrate",
        "endpoints": {
            "classify_api": CLASSIFY_API_URL,
            "push_db_api": PUSH_DB_API_URL,
            "get_aggregate_api": GET_AGGREGATE_API_URL,
            "trigger_call_api": TRIGGER_CALL_API_URL
        },
        "workflow": [
            "1. Classify crisis data",
            "2. Push to database", 
            "3. Get aggregate data",
            "4. Trigger alerts if thresholds met (tweet_count > 7 and aggregate_score > 0.75)"
        ]
    } 