"""Crisis Classification API route - Classifies crisis-related tweets and images using Gemini AI"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, Optional, List
import requests
import google.generativeai as genai
import logging
import json
import base64
import io
from PIL import Image
from config import settings
import os

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/classify-crisis")
async def classify_crisis(request_data: Dict[str, Any]):
    """
    Classify crisis-related tweets and images using Gemini AI
    
    Accepts:
    - tweet_text: str
    - image_url: str (optional)
    - image_data: str (optional, base64 encoded)
    - timestamp: str (optional)
    """
    
    try:
        # Get API key
        API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not API_KEY:
            logger.error("GOOGLE_API_KEY environment variable not set")
            raise HTTPException(status_code=500, detail="GOOGLE_API_KEY environment variable not set")

        # Configure Gemini
        genai.configure(api_key=API_KEY)

        # Extract data
        tweet_text = request_data.get('tweet_text', '')
        image_url = request_data.get('image_url', '')
        image_data = request_data.get('image_data', '')
        timestamp = request_data.get('timestamp', None)
        
        image_pil = None
        
        # Handle image data
        if image_data:
            try:
                if image_data.startswith('data:image'):
                    header, b64data = image_data.split(',', 1)
                    image_bytes = base64.b64decode(b64data)
                else:
                    image_bytes = base64.b64decode(image_data)
                image_pil = Image.open(io.BytesIO(image_bytes))
                image_url = ''  # Do not set image_url in output if using binary/base64
                logger.info("Successfully processed base64 image data")
            except Exception as e:
                logger.error(f"Failed to process image data: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

        # Download image from URL if provided
        if not image_pil and image_url:
            try:
                img_response = requests.get(image_url, timeout=10)
                img_response.raise_for_status()
                image_bytes = img_response.content
                image_pil = Image.open(io.BytesIO(image_bytes))
                logger.info(f"Successfully downloaded image from URL: {image_url}")
            except Exception as e:
                logger.warning(f"Failed to download image from URL {image_url}: {e}")
                image_pil = None

        # Validate input
        if not tweet_text and not image_pil:
            raise HTTPException(
                status_code=400, 
                detail="Either tweet_text or image (URL/base64) must be provided"
            )

        # Create prompt
        prompt = f"""
You are an expert crisis analyst. Analyze the provided tweet text and/or image to classify crisis information.

**Required Classifications:**

1. **Disaster Type**: Choose ONE from: 'fire', 'earthquake', 'hurricane', 'flood', 'tornado', 'wildfire', 'explosion', 'building_collapse', 'other_disaster', 'not_disaster'

2. **Informativeness**: Combine text and image analysis to determine: 'informative' or 'not_informative'

3. **Humanitarian Categories**: Select ALL applicable from this list:
   - 'casualties' (injured or dead people)
   - 'missing_persons' (missing or found people)  
   - 'displaced_people' (affected individuals, evacuations)
   - 'infrastructure_damage' (buildings, roads, utilities)
   - 'vehicle_damage' (cars, planes, boats damaged)
   - 'rescue_operations' (emergency response, volunteering)
   - 'donations_aid' (donation efforts, relief supplies)
   - 'emergency_services' (police, fire, medical response)
   - 'public_safety' (warnings, advisories, safety info)
   - 'none' (if no humanitarian categories apply)

4. **Location**: Extract a specific city, state, or landmark. If only a region or vague location is mentioned, infer and return the largest major city that is geographically closest to the location provided in the tweet (it may not necessarily be in California). The city should be a well-known, large city that makes sense for the context, not a small town.

5. **Damage Severity** (based on image if available): 'severe_damage', 'mild_damage', 'little_or_no_damage', 'cannot_assess'

6. **Seriousness Score**: Float from 0.0 (not serious) to 1.0 (extremely serious)

Return ONLY a valid JSON object with these exact keys:
{{
    "disaster_type": "string",
    "informativeness": "string", 
    "humanitarian_categories": ["list", "of", "categories"],
    "location": "string",
    "damage_severity": "string",
    "seriousness_score": 0.0,
    "tweet_text": "string",
    "image_url": "string"
}}

Tweet text: {tweet_text}
Image URL: {image_url}
"""

        # Generate response
        logger.info("Sending request to Gemini AI")
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        if image_pil:
            gemini_response = model.generate_content([prompt, image_pil])
        else:
            gemini_response = model.generate_content(prompt)

        response_text = gemini_response.text.strip()
        logger.info(f"Received response from Gemini: {response_text[:200]}...")
        
        # Extract JSON from response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in model response")
        
        json_str = response_text[start_idx:end_idx]
        result = json.loads(json_str)

        # Ensure all required keys are present
        required_keys = ['disaster_type', 'informativeness', 'humanitarian_categories',
                       'location', 'damage_severity', 'seriousness_score', 'tweet_text', 'image_url']
        
        for key in required_keys:
            if key not in result:
                if key == 'humanitarian_categories':
                    result[key] = ['none']
                elif key == 'tweet_text':
                    result[key] = tweet_text
                elif key == 'image_url':
                    result[key] = image_url if image_url else ''
                else:
                    result[key] = None

        if timestamp is not None:
            result['timestamp'] = timestamp

        logger.info(f"Classification successful for location: {result.get('location')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.get("/classify-crisis/health")
async def classify_crisis_health():
    """Health check for crisis classification endpoint"""
    
    # Check if Gemini API key is available
    api_key_available = bool(os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY'))
    
    return {
        "status": "healthy",
        "service": "crisis_classification",
        "gemini_api_key_configured": api_key_available,
        "supported_inputs": ["tweet_text", "image_url", "image_data (base64)"],
        "output_format": {
            "disaster_type": "string",
            "informativeness": "string",
            "humanitarian_categories": "list",
            "location": "string", 
            "damage_severity": "string",
            "seriousness_score": "float",
            "tweet_text": "string",
            "image_url": "string"
        }
    } 