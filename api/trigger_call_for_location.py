import os
import json
import sys
from supabase import create_client, Client
import requests

# Add parent directory to path for Vercel deployment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.voice_agent.trigger_call import trigger_emergency_call

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def trigger_call_for_location(location: str, disaster_type: str, timeout_minutes: int = 10):
    print(f"[DEBUG] trigger_call_for_location called with location='{location}', disaster_type='{disaster_type}'")
    # Query all users in the given location (address match)
    users = supabase.table("users").select("phone_number, location").execute()
    print(f"[DEBUG] Users query result: {users.data}")
    if not users.data:
        print("[DEBUG] No users found in Supabase for this location.")
        return {"status": "no_users_found"}
    
    called_users = []
    for user in users.data:
        loc = user.get("location", {})
        address = loc.get("address") if isinstance(loc, dict) else None
        phone_number = user.get("phone_number")
        print(f"[DEBUG] Checking user: address='{address}', phone_number='{phone_number}'")
        if address and phone_number and address.strip().lower() == location.strip().lower():
            print(f"[DEBUG] MATCH: Calling trigger_emergency_call for {phone_number} at {address}")
            # Call the trigger_emergency_call function
            result = trigger_emergency_call(
                phone_number=phone_number,
                location=address,
                natural_disaster=disaster_type,
                timeout_minutes=timeout_minutes
            )
            called_users.append({
                "phone_number": phone_number,
                "address": address,
                "result": result
            })
        else:
            print(f"[DEBUG] SKIP: No match for user {phone_number} at {address}")
    print(f"[DEBUG] Called users: {called_users}")
    return {"called_users": called_users, "count": len(called_users)}

# Vercel handler
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            print("[DEBUG] handler.do_POST called")
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            print(f"[DEBUG] Raw POST data: {post_data}")
            data = json.loads(post_data.decode('utf-8'))
            print(f"[DEBUG] Decoded JSON: {data}")
            location = data.get("location")
            disaster_type = data.get("disaster_type")
            print(f"[DEBUG] location='{location}', disaster_type='{disaster_type}'")
            if not location or not disaster_type:
                print("[DEBUG] Missing location or disaster_type in request")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing location or disaster_type"}).encode())
                return
            # Call the real logic via internal function for local, or via API for production
            if os.environ.get("VERCEL"):
                print("[DEBUG] Running in Vercel environment, making HTTP POST to Railway")
                resp = requests.post(
                    "https://calhacks-deploy-production.up.railway.app/api/v1/trigger-call-for-location",
                    json={"location": location, "disaster_type": disaster_type},
                    timeout=30
                )
                print(f"[DEBUG] HTTP POST response: {resp.status_code}, {resp.text}")
                result = resp.json() if resp.status_code == 200 else {"error": resp.text}
            else:
                print("[DEBUG] Running locally, calling trigger_call_for_location directly")
                result = trigger_call_for_location(location, disaster_type)
            print(f"[DEBUG] Final result: {result}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            print(f"[DEBUG] Exception in handler.do_POST: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
