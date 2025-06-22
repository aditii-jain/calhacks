import os
import json
import google.generativeai as genai

def extract_shelter_and_contacts_gemini(transcript):
    """
    Use Gemini to extract the shelter location and emergency contact intent from a transcript.
    """
    API_KEY = os.getenv('GOOGLE_API_KEY')
    if not API_KEY:
        raise RuntimeError("GOOGLE_API_KEY environment variable not set")
    genai.configure(api_key=API_KEY)

    prompt = f"""
You are an expert assistant. Given the following emergency call transcript, extract:
1. The most likely shelter location mentioned by the user or the AI (empty string if none).
2. Whether the user wants their emergency contacts notified (true/false/unknown).

Return ONLY a valid JSON object with these exact keys:
{{
    "shelter_location": "...",
    "wants_emergency_contacts": ...
}}

Transcript:
{transcript}
"""
    model = genai.GenerativeModel('gemini-2.5-flash')
    gemini_response = model.generate_content(prompt)
    response_text = gemini_response.text.strip()
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}') + 1
    if start_idx == -1 or end_idx == 0:
        return {"shelter_location": None, "wants_emergency_contacts": None}
    json_str = response_text[start_idx:end_idx]
    result = json.loads(json_str)
    return result

def analyze_transcript(transcript):
    """
    Analyze a conversation transcript for shelter and emergency contact intent using Gemini.
    """
    result = extract_shelter_and_contacts_gemini(transcript)
    return result

def get_google_maps_pin(shelter_location):
    """
    Generate a Google Maps pin URL for the shelter location.
    
    Args:
        shelter_location (str): The shelter name/location
        
    Returns:
        str: Google Maps URL with pin, or None if no location
    """
    if not shelter_location:
        return None
    
    # Encode the location for URL
    import urllib.parse
    encoded_location = urllib.parse.quote_plus(shelter_location)
    
    # Generate Google Maps URL with pin
    maps_url = f"https://maps.google.com/maps?q={encoded_location}&t=m&z=15"
    
    return maps_url

# Example usage
if __name__ == "__main__":
    print("🚨 Emergency Call Transcript Analyzer")
    transcript = input("Paste transcript: ")
    result = analyze_transcript(transcript)
    print("\nGemini Analysis Result:")
    print(json.dumps(result, indent=2))
    if result.get("shelter_location"):
        print("Google Maps Link:", get_google_maps_pin(result["shelter_location"]))
    if result.get("wants_emergency_contacts") is True:
        print("User wants emergency contacts notified (send SMS)")
    elif result.get("wants_emergency_contacts") is False:
        print("User does NOT want emergency contacts notified")
    else:
        print("Emergency contact intent unclear")