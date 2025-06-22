import os
import time
import requests
import json
from dotenv import load_dotenv
from .analyze_transcript import analyze_transcript, get_google_maps_pin

load_dotenv()

# Vapi API configuration
VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_BASE_URL = "https://api.vapi.ai"
TEXTBELT_API_KEY = os.getenv("TEXTBELT_API_KEY")
TEXTBELT_URL = "https://textbelt.com/text"

def make_vapi_request(method, endpoint, data=None):
    """Make a request to the Vapi API using requests library"""
    if not VAPI_API_KEY:
        raise RuntimeError("VAPI_API_KEY environment variable not set")
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{VAPI_BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Log response details for debugging
        print(f"📡 Vapi API Response: {response.status_code}")
        if response.status_code >= 400:
            print(f"📡 Error Response Body: {response.text}")
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        error_details = f"HTTP {response.status_code}: {response.text if response else 'No response body'}"
        raise Exception(f"Vapi API error - {error_details}") from e
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}") from e

# Dummy function to get emergency contacts from Supabase
def get_emergency_contacts(phone_number):
    """Get emergency contacts for a user from Supabase"""
    try:
        print(f"📱 Looking up emergency contacts for {phone_number}")
        from supabase import create_client, Client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        supabase: Client = create_client(url, key)
        
        # First, let's see what users actually exist in the database
        print(f"📱 DEBUG: Checking all users in active_users table...")
        all_users = supabase.table("active_users").select("phone_number, id, name").execute()
        print(f"📱 DEBUG: Found {len(all_users.data)} total users:")
        for user in all_users.data[:5]:  # Show first 5 users
            print(f"📱 DEBUG: User - Phone: {user.get('phone_number')}, Name: {user.get('name')}")
        
        # Try multiple phone number formats to find the user
        phone_formats = [
            phone_number,                          # Original format: +16692209078
            phone_number.replace('+1', '+'),       # Remove country code: +6692209078  
            phone_number.replace('+', ''),         # No plus: 16692209078
            phone_number.replace('+1', ''),        # No country code or plus: 6692209078
            '+1' + phone_number.replace('+', '').replace('1', '', 1) if phone_number.startswith('+1') else '+1' + phone_number.replace('+', ''),  # Ensure +1 prefix
        ]
        
        # Remove duplicates while preserving order
        phone_formats = list(dict.fromkeys(phone_formats))
        print(f"📱 DEBUG: Will try these phone formats: {phone_formats}")
        
        resp = None
        for phone_format in phone_formats:
            print(f"📱 Trying phone format: '{phone_format}'")
            resp = supabase.table("active_users").select("emergency_contacts, phone_number, name").eq("phone_number", phone_format).execute()
            print(f"📱 Query result for '{phone_format}': {len(resp.data)} users found")
            if resp.data:
                print(f"📱 ✅ Found user with phone format: '{phone_format}' - User: {resp.data[0].get('name')}")
                break
        
        if not resp or not resp.data:
            print(f"📱 ❌ No user found with any phone format.")
            print(f"📱 ❌ Searched for: {phone_formats}")
            print(f"📱 ❌ Available phone numbers in DB: {[u.get('phone_number') for u in all_users.data[:10]]}")
            return []
            
        print(f"📱 Supabase response: {resp.data}")
        
        if resp.data and len(resp.data) > 0:
            user_data = resp.data[0]
            emergency_contacts = user_data.get("emergency_contacts")
            print(f"📱 Raw emergency_contacts data: {emergency_contacts}")
            
            if emergency_contacts:
                if isinstance(emergency_contacts, list):
                    # Handle list of dicts with 'phone' keys
                    phone_numbers = []
                    for contact in emergency_contacts:
                        if isinstance(contact, dict) and "phone" in contact:
                            phone_numbers.append(contact["phone"])
                        elif isinstance(contact, str):
                            # Handle direct phone number strings
                            phone_numbers.append(contact)
                    print(f"📱 Extracted phone numbers: {phone_numbers}")
                    return phone_numbers
                else:
                    print(f"📱 emergency_contacts is not a list: {type(emergency_contacts)}")
            else:
                print(f"📱 No emergency_contacts field found or it's empty")
        else:
            print(f"📱 No user found with phone number {phone_number}")
            
    except Exception as e:
        print(f"📱 Error getting emergency contacts: {e}")
        import traceback
        traceback.print_exc()
    
    return []

def get_user_name(phone_number):
    """Get user's name from Supabase active_users table"""
    try:
        print(f"📱 Looking up user name for {phone_number}")
        from supabase import create_client, Client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        supabase: Client = create_client(url, key)
        
        # Try multiple phone number formats to find the user
        phone_formats = [
            phone_number,                          # Original format: +16692209078
            phone_number.replace('+1', '+'),       # Remove country code: +6692209078  
            phone_number.replace('+', ''),         # No plus: 16692209078
            phone_number.replace('+1', ''),        # No country code or plus: 6692209078
            '+1' + phone_number.replace('+', '').replace('1', '', 1) if phone_number.startswith('+1') else '+1' + phone_number.replace('+', ''),  # Ensure +1 prefix
        ]
        
        # Remove duplicates while preserving order
        phone_formats = list(dict.fromkeys(phone_formats))
        print(f"📱 DEBUG: Will try these phone formats for name lookup: {phone_formats}")
        
        resp = None
        for phone_format in phone_formats:
            print(f"📱 Trying phone format for name: '{phone_format}'")
            resp = supabase.table("active_users").select("name, phone_number").eq("phone_number", phone_format).execute()
            print(f"📱 Name query result for '{phone_format}': {len(resp.data)} users found")
            if resp.data:
                user_name = resp.data[0].get('name')
                print(f"📱 ✅ Found user name: '{user_name}' for phone format: '{phone_format}'")
                return user_name
        
        print(f"📱 ❌ No user name found for {phone_number}")
        return None
            
    except Exception as e:
        print(f"📱 Error getting user name: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def send_sms(phone, message):
    """Send SMS using TextBelt API"""
    try:
        print(f"📱 Attempting to send SMS to {phone}")
        print(f"📱 Message: {message}")
        
        # Check if TextBelt API key is available
        if not TEXTBELT_API_KEY:
            print(f"❌ TEXTBELT_API_KEY environment variable not set")
            return {"success": False, "error": "TEXTBELT_API_KEY not configured"}
        
        print(f"📱 Using TextBelt API key: {TEXTBELT_API_KEY[:10]}...")
        
        resp = requests.post(
            TEXTBELT_URL,
            data={
                'phone': phone,
                'message': message,
                'key': TEXTBELT_API_KEY
            },
            timeout=10
        )
        
        print(f"📱 TextBelt response status: {resp.status_code}")
        print(f"📱 TextBelt response: {resp.text}")
        
        result = resp.json()
        
        if result.get("success"):
            print(f"✅ SMS sent successfully to {phone}")
        else:
            print(f"❌ SMS failed to {phone}: {result}")
            
        return result
        
    except Exception as e:
        print(f"❌ Error sending SMS to {phone}: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def trigger_emergency_call(phone_number: str, location: str, natural_disaster: str, timeout_minutes: int = 10) -> dict:
    """
    Trigger an emergency call and return user preferences and shelter location.
    
    Args:
        phone_number (str): Phone number to call (E.164 format, e.g. +1234567890)
        location (str): Location of the emergency (e.g. "Los Angeles", "San Francisco")
        natural_disaster (str): Type of disaster (e.g. "wildfire", "earthquake", "flood")
        timeout_minutes (int): How long to wait for call completion (default: 10 minutes)
    
    Returns:
        dict: Call result with status, preferences, and shelter information
        {
            "status": "success" | "error",
            "call_id": str | None,
            "send_directions": bool,
            "contact_emergency_contacts": bool,
            "google_maps_pin": str | None,
            "error": str | None
        }
    """
    
    # Configuration
    assistant_id = "d97df5ae-d4b9-4644-9836-e22a19e0fbea"
    phone_number_id = "4107aab6-6685-4a40-9344-586b9490b711"
    
    # Validate phone number format
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    # Emergency scenario variables
    emergency_variables = {
        "natural_disaster": natural_disaster,
        "location": location
    }
    
    print(f"🚨 Triggering emergency call for {natural_disaster} in {location}")
    print(f"📞 Calling: {phone_number}")
    
    try:
        # Create the call using REST API
        call_data = {
            "assistantId": assistant_id,
            "phoneNumberId": phone_number_id,
            "customer": {
                "number": phone_number
            },
            "assistantOverrides": {
                "variableValues": emergency_variables
            }
        }
        
        print(f"📞 Making Vapi call with data: {json.dumps(call_data, indent=2)}")
        call_response = make_vapi_request("POST", "/call", call_data)
        call_id = call_response.get("id")
        
        if not call_id:
            raise Exception("Failed to get call ID from Vapi response")
        
        print(f"✅ Call initiated: {call_id}")
        print(f"⏳ Waiting for call completion (timeout: {timeout_minutes} minutes)...")
        
        # Wait for call completion and get transcript
        transcript = _wait_for_transcript(call_id, timeout_minutes)
        
        if not transcript:
            print("❌ No transcript available - returning default values")
            return {
                "status": "success",
                "call_id": call_id,
                "send_directions": False,
                "contact_emergency_contacts": False,
                "google_maps_pin": None,
                "error": "No transcript available"
            }
        
        # Analyze transcript
        print("📋 Analyzing transcript...")
        analysis = analyze_transcript(transcript)
        
        # Extract boolean results
        shelter_locations = analysis.get('shelter_locations', [])
        send_directions = bool(shelter_locations)
        contact_emergency = analysis.get('wants_emergency_contacts') is True
        
        # Generate Google Maps pin for first shelter (for backward compatibility)
        shelter_location = shelter_locations[0] if shelter_locations else None
        google_maps_pin = get_google_maps_pin(shelter_location) if shelter_location else None
        
        print(f"📊 Results:")
        print(f"   Send Directions: {send_directions}")
        print(f"   Contact Emergency Contacts: {contact_emergency}")
        print(f"   Shelter Locations from transcript: {shelter_locations}")
        
        if shelter_locations:
            # Send SMS to user with all shelter names from transcript (no URLs)
            if len(shelter_locations) == 1:
                shelter_text = shelter_locations[0]
            elif len(shelter_locations) <= 3:
                shelter_text = ", ".join(shelter_locations)
            else:
                # Limit to first 3 shelters
                shelter_text = ", ".join(shelter_locations[:3])
            
            print(f"   Sending shelter info: {shelter_text}")
            send_sms(phone_number, f"🏠 Emergency Shelters: {shelter_text}")
        
        if contact_emergency:
            print(f"📱 User wants emergency contacts notified - fetching contacts...")
            # Get emergency contacts from Supabase
            emergency_contacts = get_emergency_contacts(phone_number)
            print(f"📱 Found {len(emergency_contacts)} emergency contacts: {emergency_contacts}")
            
            if emergency_contacts:
                # Get user's name for the emergency alert message
                user_name = get_user_name(phone_number)
                contact_identifier = user_name if user_name else phone_number
                
                for contact in emergency_contacts:
                    print(f"📱 Sending SMS to emergency contact: {contact}")
                    # Send simple emergency alert without URLs, using user's name
                    sms_result = send_sms(contact, f"🚨 Emergency Alert: {contact_identifier} may need assistance due to {natural_disaster} in {location}. Please check on them.")
                    print(f"📱 SMS result for {contact}: {sms_result}")
            else:
                print(f"📱 No emergency contacts found for {phone_number}")
        else:
            print(f"📱 User does not want emergency contacts notified")
        
        return {
            "status": "success",
            "call_id": call_id,
            "send_directions": send_directions,
            "contact_emergency_contacts": contact_emergency,
            "google_maps_pin": google_maps_pin,
            "error": None
        }
        
    except Exception as error:
        print(f"❌ Error during emergency call: {error}")
        return {
            "status": "error",
            "call_id": None,
            "send_directions": False,
            "contact_emergency_contacts": False,
            "google_maps_pin": None,
            "error": str(error)
        }

def _wait_for_transcript(call_id: str, timeout_minutes: int) -> str:
    """
    Wait for call completion and return transcript.
    
    Args:
        call_id (str): The call ID to monitor
        timeout_minutes (int): Timeout in minutes
        
    Returns:
        str: The call transcript, or None if not available
    """
    
    timeout_seconds = timeout_minutes * 60
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        try:
            call_response = make_vapi_request("GET", f"/call/{call_id}")
            status = call_response.get("status")
            
            # Check if call is completed
            if status in ['completed', 'ended', 'finished']:
                print(f"✅ Call completed with status: {status}")
                
                # Check if transcript is available
                transcript = call_response.get("transcript")
                if transcript:
                    return transcript
                else:
                    print("⚠️ Call completed but transcript not ready yet, waiting...")
                    time.sleep(5)
                    
            elif status in ['failed', 'error']:
                print(f"❌ Call failed with status: {status}")
                return None
                
            else:
                print(f"📞 Call in progress... Status: {status or 'unknown'}")
                time.sleep(15)  # Check every 15 seconds
                
        except Exception as e:
            print(f"Error checking call status: {e}")
            time.sleep(15)
    
    print(f"⏰ Timeout reached ({timeout_minutes} minutes)")
    
    # One final check for transcript
    try:
        call_response = make_vapi_request("GET", f"/call/{call_id}")
        transcript = call_response.get("transcript")
        if transcript:
            print("📋 Found transcript on final check!")
            return transcript
    except Exception as e:
        print(f"Final transcript check failed: {e}")
    
    return None



# Example usage function
def example_usage():
    """Example of how to use the trigger_emergency_call function."""
    
    phone_number = input("Enter phone number to test (e.g., +1234567890): ").strip()
    
    if not phone_number:
        print("❌ No phone number provided")
        return
    
    # Test scenarios
    scenarios = [
        ("Los Angeles", "wildfire"),
        ("San Francisco", "earthquake"),
        ("Miami", "hurricane")
    ]
    
    print(f"\n🧪 Available test scenarios:")
    for i, (location, disaster) in enumerate(scenarios, 1):
        print(f"{i}. {disaster.title()} in {location}")
    
    choice = input(f"\nSelect scenario (1-{len(scenarios)}) or enter custom: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(scenarios):
        location, natural_disaster = scenarios[int(choice) - 1]
    else:
        location = input("Enter location: ").strip()
        natural_disaster = input("Enter disaster type: ").strip()
    
    if not location or not natural_disaster:
        print("❌ Missing location or disaster type")
        return
    
    print(f"\n🚨 Testing emergency call:")
    print(f"Location: {location}")
    print(f"Disaster: {natural_disaster}")
    print(f"Phone: {phone_number}")
    
    confirm = input(f"\nProceed with call? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Cancelled")
        return
    
    # Trigger the call
    result = trigger_emergency_call(
        phone_number=phone_number,
        location=location,
        natural_disaster=natural_disaster,
        timeout_minutes=15
    )
    
    print(f"\n📊 Final Results:")
    print(f"   🟢 Status: {result.get('status')}")
    print(f"   📞 Call ID: {result.get('call_id', 'None')}")
    print(f"   📍 Send Directions: {result.get('send_directions')}")
    print(f"   📱 Contact Emergency: {result.get('contact_emergency_contacts')}")
    print(f"   🗺️ Google Maps Pin: {result.get('google_maps_pin') or 'None'}")
    if result.get('error'):
        print(f"   ❌ Error: {result.get('error')}")

if __name__ == "__main__":
    example_usage()