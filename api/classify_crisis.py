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
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import io
from PIL import Image

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get API key
            API_KEY = os.getenv('GOOGLE_API_KEY')
            if not API_KEY:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "GOOGLE_API_KEY environment variable not set"}).encode())
                return

            # Configure Gemini
            genai.configure(api_key=API_KEY)

            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON in request body"}).encode())
                return

            tweet_text = request_data.get('tweet_text', '')
            image_url = request_data.get('image_url', '')

            if not tweet_text and not image_url:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Either tweet_text or image_url must be provided"}).encode())
                return

            # Download image if URL provided
            image_bytes = None
            image_pil = None
            if image_url:
                try:
                    img_response = requests.get(image_url, timeout=10)
                    img_response.raise_for_status()
                    image_bytes = img_response.content
                    image_pil = Image.open(io.BytesIO(image_bytes))
                except Exception as e:
                    print(f"Failed to download image: {e}")
                    image_pil = None
            else:
                image_pil = None

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

            # Generate response
            model = genai.GenerativeModel('gemini-2.5-flash')
            if image_pil:
                gemini_response = model.generate_content([prompt, image_pil])
            else:
                gemini_response = model.generate_content(prompt)

            response_text = gemini_response.text.strip()
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in model response")
            
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)

            # Ensure all required keys are present
            required_keys = ['disaster_type', 'informativeness', 'humanitarian_categories',
                           'location', 'damage_severity', 'seriousness_score']
            for key in required_keys:
                if key not in result:
                    result[key] = None if key != 'humanitarian_categories' else ['none']

            # Send successful response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Classification failed: {str(e)}"}).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        # Simple health check
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "Crisis Classification API is running"}).encode())