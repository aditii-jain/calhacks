import os
import json
import requests
from http.server import BaseHTTPRequestHandler

CLASSIFY_API_URL = "https://calhack4.vercel.app/api/classify_crisis"
PUSH_DB_API_URL = "https://calhack4.vercel.app/api/push_classification_db"

class handler(BaseHTTPRequestHandler):
    def trigger_crisis_alert(self, aggregate_data):
        """
        Triggers emergency calls for all users in the affected location by calling the API endpoint.
        """
        import requests
        location = aggregate_data.get("location")
        disaster_type = aggregate_data.get("disaster_type")
        if not location or not disaster_type:
            return False
        try:
            resp = requests.post(
                "https://calhack4.vercel.app/api/trigger_call_for_location",
                json={"location": location, "disaster_type": disaster_type},
                timeout=30
            )
            if resp.status_code == 200:
                result = resp.json()
                return bool(result and result.get("count", 0) > 0)
            return False
        except Exception:
            return False

    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                input_data = json.loads(post_data.decode('utf-8'))
            except Exception:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON in request body"}).encode())
                return

            # Forward to classifier API
            resp = requests.post(CLASSIFY_API_URL, json=input_data, timeout=60)
            if resp.status_code != 200:
                self.send_response(resp.status_code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Classification API failed", "details": resp.text}).encode())
                return

            classification = resp.json()

            # Forward to push_classification_db API
            db_resp = requests.post(PUSH_DB_API_URL, json=classification, timeout=30)
            if db_resp.status_code != 200:
                inserted = False
                db_result = {"error": db_resp.text}
            else:
                db_result = db_resp.json()
                inserted = db_result.get("inserted", False)

            if inserted:
                agg_resp = requests.post("https://calhack4.vercel.app/api/get_aggregate", json=classification, timeout=30)
                agg_result = agg_resp.json() if agg_resp.status_code == 200 else {"error": agg_resp.text}
                # New step: check tweet_count and aggregate_score, trigger alert if needed
                alert_triggered = False
                if agg_resp.status_code == 200 and "error" not in agg_result:
                    tweet_count = agg_result.get("tweet_count", 0)
                    aggregate_score = agg_result.get("aggregate_score", 0)
                    if tweet_count > 7 and aggregate_score > 0.75:
                        print(f"[DEBUG] About to trigger crisis alert for: {agg_result}")
                        alert_triggered = self.trigger_crisis_alert(agg_result)
                        print(f"[DEBUG] Alert triggered result: {alert_triggered}")
            else:
                agg_result = None
                alert_triggered = False

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "classification": classification,
                "inserted": inserted,
                "aggregate": agg_result,
                "alert_triggered": alert_triggered
            }, indent=2).encode())

        except Exception as e:
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