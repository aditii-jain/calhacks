import os
import time
import requests
from vapi import Vapi
from dotenv import load_dotenv
from .analyze_transcript import analyze_transcript, get_google_maps_pin

load_dotenv()

# Initialize the Vapi client
try:
    client = Vapi(token=os.getenv("VAPI_API_KEY"))
    print("Successfully connected to Vapi client")
except Exception as error:
    print(f"Error connecting to Vapi client: {error}")
    raise error

TEXTBELT_API_KEY = os.getenv("TEXTBELT_API_KEY") or "558eda4c96a2cc3f0eb6d8f0d12fc6a4b29eb98dKUoSGxDY8Sdpm4NRujkHGqFp1"
TEXTBELT_URL = "https://textbelt.com/text"

# Dummy function to get emergency contacts from Supabase
# Replace with real Supabase query
def get_emergency_contacts(phone_number):
    # Query Supabase for the user with the given phone number
    from supabase import create_client, Client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    supabase: Client = create_client(url, key)
    resp = supabase.table("users").select("emergency_contacts").eq("phone_number", phone_number).execute()
    if resp.data and resp.data[0].get("emergency_contacts"):
        contacts = resp.data[0]["emergency_contacts"]
        # contacts is expected to be a list of dicts with 'phone' keys
        return [c["phone"] for c in contacts if "phone" in c]
    return []

def send_sms(phone, message):
    resp = requests.post(
        TEXTBELT_URL,
        data={
            'phone': phone,
            'message': message,
            'key': TEXTBELT_API_KEY
        }
    )
    print(f"[DEBUG] SMS sent to {phone}: {resp.text}")
    return resp.json()

def trigger_emergency_call(phone_number: str, location: str, natural_disaster: str, timeout_minutes: int = 10) -> tuple[bool, bool, str]:
    """
    Trigger an emergency call and return user preferences and shelter location.
    
    Args:
        phone_number (str): Phone number to call (E.164 format, e.g. +1234567890)
        location (str): Location of the emergency (e.g. "Los Angeles", "San Francisco")
        natural_disaster (str): Type of disaster (e.g. "wildfire", "earthquake", "flood")
        timeout_minutes (int): How long to wait for call completion (default: 10 minutes)
    
    Returns:
        tuple[bool, bool, str]: (send_directions, contact_emergency_contacts, google_maps_pin)
        - send_directions: True if user wants shelter directions
        - contact_emergency_contacts: True if user wants emergency contacts notified
        - google_maps_pin: Google Maps URL for shelter location, or None if not found
    """
    
    # Configuration
    assistant_id = "f761f81a-656f-4695-8ea9-c8640a0d1b37"
    phone_number_id = "e11d54bf-6836-451d-a100-37245567a502"
    
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
        # Create the call
        call = client.calls.create(
            assistant_id=assistant_id,
            phone_number_id=phone_number_id,
            customer={
                "number": phone_number
            },
            assistant_overrides={
                "variable_values": emergency_variables
            }
        )
        
        print(f"✅ Call initiated: {call.id}")
        print(f"⏳ Waiting for call completion (timeout: {timeout_minutes} minutes)...")
        
        # Wait for call completion and get transcript
        transcript = _wait_for_transcript(call.id, timeout_minutes)
        
        if not transcript:
            print("❌ No transcript available - returning default values")
            return (False, False, None)
        
        # Analyze transcript
        print("📋 Analyzing transcript...")
        analysis = analyze_transcript(transcript)
        
        # Extract boolean results
        send_directions = bool(analysis.get('shelter_location'))
        contact_emergency = analysis.get('wants_emergency_contacts') is True
        
        # Extract shelter location and generate Google Maps pin
        shelter_location = analysis.get('shelter_location')
        google_maps_pin = get_google_maps_pin(shelter_location) if shelter_location else None
        
        print(f"📊 Results:")
        print(f"   Send Directions: {send_directions}")
        print(f"   Contact Emergency Contacts: {contact_emergency}")
        print(f"   Shelter Location: {shelter_location or 'Not specified'}")
        if google_maps_pin:
            print(f"   Google Maps Pin: {google_maps_pin}")
            # Send SMS to user with shelter directions
            send_sms(phone_number, f"🚨 Emergency Shelter Directions: {google_maps_pin}")
        
        if contact_emergency:
            # Dummy: get emergency contacts from Supabase
            emergency_contacts = get_emergency_contacts(phone_number)
            for contact in emergency_contacts:
                send_sms(contact, f"🚨 Emergency: {phone_number} may need help. Location: {location} - {google_maps_pin or ''}")
        
        return (send_directions, contact_emergency, google_maps_pin)
        
    except Exception as error:
        print(f"❌ Error during emergency call: {error}")
        return (False, False, None)

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
            call = client.calls.get(call_id)
            
            # Check if call is completed
            if hasattr(call, 'status') and call.status in ['completed', 'ended', 'finished']:
                print(f"✅ Call completed with status: {call.status}")
                
                # Check if transcript is available
                if hasattr(call, 'transcript') and call.transcript:
                    return call.transcript
                else:
                    print("⚠️ Call completed but transcript not ready yet, waiting...")
                    time.sleep(5)
                    
            elif hasattr(call, 'status') and call.status in ['failed', 'error']:
                print(f"❌ Call failed with status: {call.status}")
                return None
                
            else:
                print(f"📞 Call in progress... Status: {getattr(call, 'status', 'unknown')}")
                time.sleep(15)  # Check every 15 seconds
                
        except Exception as e:
            print(f"Error checking call status: {e}")
            time.sleep(15)
    
    print(f"⏰ Timeout reached ({timeout_minutes} minutes)")
    
    # One final check for transcript
    try:
        call = client.calls.get(call_id)
        if hasattr(call, 'transcript') and call.transcript:
            print("📋 Found transcript on final check!")
            return call.transcript
    except:
        pass
    
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
    send_directions, contact_emergency, google_maps_pin = trigger_emergency_call(
        phone_number=phone_number,
        location=location, 
        natural_disaster=natural_disaster,
        timeout_minutes=12
    )
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Send Directions: {send_directions}")
    print(f"Contact Emergency Contacts: {contact_emergency}")
    print(f"Google Maps Pin: {google_maps_pin or 'No shelter location found'}")
    
    # Show practical usage example
    if send_directions and google_maps_pin:
        print(f"\n📱 Example SMS to send:")
        print(f"🚨 Emergency Shelter Directions")
        print(f"📍 Location: {google_maps_pin}")
        print(f"Tap to open in Google Maps")
    
    return (send_directions, contact_emergency, google_maps_pin)

if __name__ == "__main__":
    example_usage()