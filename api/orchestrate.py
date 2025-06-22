import os
import json
import requests
from http.server import BaseHTTPRequestHandler

CLASSIFY_API_URL = "https://calhack4.vercel.app/api/classify_crisis"
PUSH_DB_API_URL = "https://calhack4.vercel.app/api/push_classification_db"

class handler(BaseHTTPRequestHandler):
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
            else:
                agg_result = None

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "classification": classification,
                "inserted": inserted,
                "aggregate": agg_result
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