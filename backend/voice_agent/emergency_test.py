import os
import time
from vapi import Vapi
from dotenv import load_dotenv
from analyze_transcript import analyze_transcript, print_analysis

load_dotenv()

# Initialize the Vapi client
try:
    client = Vapi(token=os.getenv("VAPI_API_KEY"))
    print("Successfully connected to Vapi client")
except Exception as error:
    print(f"Error connecting to Vapi client: {error}")
    raise error

def wait_for_call_completion_and_analyze(call_id: str, timeout_minutes: int = 10):
    """Wait for a call to complete and then analyze the transcript."""
    
    print(f"\n🔍 Monitoring call {call_id} for completion...")
    print(f"Timeout: {timeout_minutes} minutes")
    
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
                    print(f"\n📋 Transcript found! Analyzing emergency response...")
                    print("=" * 60)
                    print_analysis(call.transcript)
                    return call
                else:
                    print("⚠️ Call completed but no transcript available yet. Waiting a bit more...")
                    time.sleep(5)
                    
            elif hasattr(call, 'status') and call.status in ['failed', 'error']:
                print(f"❌ Call failed with status: {call.status}")
                return call
                
            else:
                print(f"📞 Call in progress... Status: {getattr(call, 'status', 'unknown')}")
                time.sleep(15)  # Check every 15 seconds
                
        except Exception as e:
            print(f"Error checking call status: {e}")
            time.sleep(15)
    
    print(f"⏰ Timeout reached ({timeout_minutes} minutes). Checking one last time...")
    try:
        call = client.calls.get(call_id)
        if hasattr(call, 'transcript') and call.transcript:
            print(f"\n📋 Final transcript check - analyzing...")
            print_analysis(call.transcript)
        else:
            print("📝 No transcript available yet. You can check later with post_call_analysis.py")
    except:
        pass
    
    return None

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
        
        # Ask if user wants to wait for transcript analysis
        analyze_prompt = input(f"\n🔍 Do you want to wait for the call to complete and analyze the transcript? (Y/n): ").strip().lower()
        
        if analyze_prompt not in ['n', 'no']:
            print(f"\n⏳ Starting call monitoring...")
            print(f"💡 Take the call and respond naturally. Analysis will start when the call ends.")
            wait_for_call_completion_and_analyze(call.id, timeout_minutes=15)
        else:
            print(f"\n✅ Call started. Use post_call_analysis.py later to analyze the transcript.")
            print(f"Call ID for future reference: {call.id}")
        
        return call
        
    except Exception as error:
        print(f"❌ Error making emergency call: {error}")
        raise error

if __name__ == "__main__":
    make_emergency_call() 