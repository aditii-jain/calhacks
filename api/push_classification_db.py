import os
import requests
import json
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client

# Supabase credentials from environment variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

table_name = "crisis_tweets_classification"

def ensure_table_exists():
    ddl = f'''
    create table if not exists {table_name} (
        id serial primary key,
        disaster_type text,
        informativeness text,
        humanitarian_categories jsonb,
        location text,
        damage_severity text,
        seriousness_score float8,
        tweet_text text unique,
        image_url text,
        timestamp text
    );
    '''
    try:
        supabase.postgrest.rpc("execute_sql", {"sql": ddl}).execute()
    except Exception as e:
        # Ignore if already exists or if function not available
        pass

def push_classification_to_db(data):
    ensure_table_exists()
    # Check if tweet_text exists
    existing = supabase.table(table_name).select("id").eq("tweet_text", data["tweet_text"]).execute()
    if existing.data:
        print("Tweet already exists, not inserting.")
        return False
    else:
        insert_data = {k: data.get(k) for k in [
            "disaster_type", "informativeness", "humanitarian_categories", "location",
            "damage_severity", "seriousness_score", "tweet_text", "image_url", "timestamp"
        ]}
        res = supabase.table(table_name).insert(insert_data).execute()
        print("Inserted:", res.data)
        return True

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON in request body"}).encode())
                return

            inserted = push_classification_to_db(data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"inserted": inserted}).encode())
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