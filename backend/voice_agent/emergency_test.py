import os
from vapi import Vapi
from dotenv import load_dotenv

load_dotenv()

# Initialize the Vapi client
try:
    client = Vapi(token=os.getenv("VAPI_API_KEY"))
    print("Successfully connected to Vapi client")
except Exception as error:
    print(f"Error connecting to Vapi client: {error}")
    raise error

def make_emergency_call():
    """Make an emergency test call with the assistant and variables."""
    # Configuration
    assistant_id = "f761f81a-656f-4695-8ea9-c8640a0d1b37"
    phone_number_id = "e11d54bf-6836-451d-a100-37245567a502"
    
    # Prompt user for phone number
    print("🚨 Emergency Assistant Test Call 🚨")
    print("=" * 50)
    print("This will call your phone number with a simulated emergency alert.")
    print("The assistant will use variables: {{natural_disaster}} and {{location}}")
    print("=" * 50)
    
    test_phone_number = input("\nEnter the phone number to call (e.g., +1234567890): ").strip()
    
    if not test_phone_number:
        print("❌ No phone number provided. Exiting.")
        return None
    
    # Validate basic format
    if not test_phone_number.startswith('+'):
        print("⚠️  Adding '+' prefix to phone number...")
        test_phone_number = '+' + test_phone_number
    
    # Emergency scenario variables
    emergency_variables = {
        "natural_disaster": "wildfire",
        "location": "Los Angeles"
    }
    
    print(f"\n📞 Making emergency test call...")
    print(f"Assistant ID: {assistant_id}")
    print(f"Phone Number ID: {phone_number_id}")
    print(f"Calling: {test_phone_number}")
    print(f"Variables: {emergency_variables}")
    
    # Confirm before making the call
    confirm = input(f"\nAre you sure you want to call {test_phone_number}? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Call cancelled.")
        return None
    
    try:
        # Create the call
        call = client.calls.create(
            assistant_id=assistant_id,
            phone_number_id=phone_number_id,
            customer={
                "number": test_phone_number
            },
            assistant_overrides={
                "variable_values": emergency_variables
            }
        )
        
        print(f"\n✅ Emergency call initiated successfully!")
        print(f"Call ID: {call.id}")
        print(f"\n📱 The call should start shortly on {test_phone_number}")
        print(f"The assistant will replace {{{{natural_disaster}}}} with '{emergency_variables['natural_disaster']}' and {{{{location}}}} with '{emergency_variables['location']}'")
        print(f"\n💡 You can respond 'yes' to hear about shelter options or 'no' to decline.")
        
        return call
        
    except Exception as error:
        print(f"❌ Error making emergency call: {error}")
        raise error

if __name__ == "__main__":
    make_emergency_call() 