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

def get_call_details(call_id: str):
    """Get details of a specific call including transcript."""
    try:
        call = client.calls.get(call_id)
        return call
    except Exception as error:
        print(f"Error getting call details: {error}")
        raise error

def wait_for_call_completion(call_id: str, timeout_minutes: int = 10):
    """Wait for a call to complete and then analyze the transcript."""
    
    print(f"⏳ Waiting for call {call_id} to complete...")
    print(f"Timeout: {timeout_minutes} minutes")
    
    timeout_seconds = timeout_minutes * 60
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        try:
            call = get_call_details(call_id)
            
            # Check if call is completed
            if hasattr(call, 'status') and call.status in ['completed', 'ended', 'finished']:
                print(f"✅ Call completed with status: {call.status}")
                
                # Check if transcript is available
                if hasattr(call, 'transcript') and call.transcript:
                    print(f"\n📋 Transcript found! Analyzing...")
                    print_analysis(call.transcript)
                    return call
                else:
                    print("⚠️ Call completed but no transcript available yet. Waiting a bit more...")
                    time.sleep(5)
                    
            elif hasattr(call, 'status') and call.status in ['failed', 'error']:
                print(f"❌ Call failed with status: {call.status}")
                return call
                
            else:
                print(f"📞 Call still in progress... Status: {getattr(call, 'status', 'unknown')}")
                time.sleep(10)  # Check every 10 seconds
                
        except Exception as e:
            print(f"Error checking call status: {e}")
            time.sleep(10)
    
    print(f"⏰ Timeout reached ({timeout_minutes} minutes). Call may still be in progress.")
    return None

def analyze_recent_calls(limit: int = 5):
    """Analyze transcripts from recent calls."""
    
    try:
        print(f"🔍 Fetching last {limit} calls...")
        calls = client.calls.list(limit=limit)
        
        for call in calls:
            print(f"\n{'='*60}")
            print(f"📞 Call ID: {call.id}")
            print(f"Status: {getattr(call, 'status', 'unknown')}")
            print(f"Created: {getattr(call, 'created_at', 'unknown')}")
            
            if hasattr(call, 'transcript') and call.transcript:
                print(f"📋 Analyzing transcript...")
                analysis = analyze_transcript(call.transcript)
                
                # Print summary
                emergency_status = "✅ WANTS" if analysis['wants_emergency_contacts'] else "❌ DECLINED" if analysis['wants_emergency_contacts'] is False else "❓ UNCLEAR"
                shelter_status = "✅ WANTS" if analysis['wants_shelter_directions'] else "❌ DECLINED" if analysis['wants_shelter_directions'] is False else "❓ UNCLEAR"
                
                print(f"📊 Quick Summary:")
                print(f"   Emergency Contacts: {emergency_status}")
                print(f"   Shelter Directions: {shelter_status}")
                
                if analysis['key_phrases']:
                    print(f"   Key Findings: {', '.join(analysis['key_phrases'])}")
            else:
                print("📝 No transcript available for this call")
        
    except Exception as e:
        print(f"Error analyzing recent calls: {e}")

def monitor_call_and_analyze(call_id: str):
    """Monitor a specific call and analyze when it completes."""
    
    print(f"🚨 Emergency Call Monitor Started")
    print(f"Call ID: {call_id}")
    print("="*50)
    
    # Wait for call to complete and analyze
    completed_call = wait_for_call_completion(call_id, timeout_minutes=15)
    
    if completed_call:
        print(f"\n✅ Analysis complete for call {call_id}")
    else:
        print(f"\n⚠️ Could not complete analysis for call {call_id}")

if __name__ == "__main__":
    print("🚨 Post-Call Analysis Tool")
    print("Choose an option:")
    print("1. Monitor a specific call ID")
    print("2. Analyze recent calls")
    print("3. Get details of a specific call")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        call_id = input("Enter call ID to monitor: ").strip()
        if call_id:
            monitor_call_and_analyze(call_id)
        else:
            print("❌ No call ID provided")
            
    elif choice == "2":
        limit = input("How many recent calls to analyze? (default 5): ").strip()
        limit = int(limit) if limit.isdigit() else 5
        analyze_recent_calls(limit)
        
    elif choice == "3":
        call_id = input("Enter call ID: ").strip()
        if call_id:
            try:
                call = get_call_details(call_id)
                print(f"\n📞 Call Details:")
                print(f"ID: {call.id}")
                print(f"Status: {getattr(call, 'status', 'unknown')}")
                print(f"Created: {getattr(call, 'created_at', 'unknown')}")
                
                if hasattr(call, 'transcript') and call.transcript:
                    print(f"\n📋 Transcript available - analyzing...")
                    print_analysis(call.transcript)
                else:
                    print(f"\n📝 No transcript available yet")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ No call ID provided")
    
    else:
        print("❌ Invalid choice") 