"""
Simplified Crisis Classification API
==================================
Vercel function for classifying crisis-related tweets and images.
Place this file at: api/classify_crisis.py
"""

import os
import json
import requests
import google.generativeai as genai

def handler(request, response):
    try:
        if request.method != "POST":
            response.status_code = 405
            return response.send("Method Not Allowed")

        API_KEY = os.getenv('GOOGLE_API_KEY')
        if not API_KEY:
            response.status_code = 500
            return response.send("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=API_KEY)

        request_data = request.json()
        tweet_text = request_data.get('tweet_text', '')
        image_url = request_data.get('image_url', '')

        if not tweet_text and not image_url:
            response.status_code = 400
            return response.send("Either tweet_text or image_url must be provided")

        image_bytes = None
        if image_url:
            try:
                img_response = requests.get(image_url, timeout=10)
                img_response.raise_for_status()
                image_bytes = img_response.content
            except Exception as e:
                print(f"Failed to download image: {e}")

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

4. **Location**: Extract specific location (city, state, landmark) or return "no_location_identified"

5. **Damage Severity** (based on image if available): 'severe_damage', 'mild_damage', 'little_or_no_damage', 'cannot_assess'

6. **Seriousness Score**: Float from 0.0 (not serious) to 1.0 (extremely serious)

Return ONLY a valid JSON object with these exact keys:
{{
    "disaster_type": "string",
    "informativeness": "string", 
    "humanitarian_categories": ["list", "of", "categories"],
    "location": "string",
    "damage_severity": "string",
    "seriousness_score": 0.0
}}

Tweet text: {tweet_text}
Image URL: {image_url}
"""

        model = genai.GenerativeModel('gemini-2.5-flash')
        if image_bytes:
            gemini_response = model.generate_content([prompt, image_bytes])
        else:
            gemini_response = model.generate_content(prompt)

        response_text = gemini_response.text.strip()
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in model response")
        json_str = response_text[start_idx:end_idx]
        result = json.loads(json_str)

        required_keys = ['disaster_type', 'informativeness', 'humanitarian_categories',
                         'location', 'damage_severity', 'seriousness_score']
        for key in required_keys:
            if key not in result:
                result[key] = None if key != 'humanitarian_categories' else ['none']

        response.status_code = 200
        response.headers["Content-Type"] = "application/json"
        return response.send(json.dumps(result, indent=2))

    except json.JSONDecodeError:
        response.status_code = 400
        return response.send("Invalid JSON in request body")
    except Exception as e:
        response.status_code = 500
        return response.send(f"Classification failed: {str(e)}")