import os
import json
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)
agg_table = "crisis_location_aggregate"

def calc_aggregate_score(data):
    seriousness = float(data.get("seriousness_score", 0))
    informativeness = 1.0 if data.get("informativeness") == "informative" else 0.0
    damage_map = {
        "severe_damage": 1.0,
        "mild_damage": 0.5,
        "little_or_no_damage": 0.1,
        "cannot_assess": 0.0
    }
    damage = damage_map.get(data.get("damage_severity", ""), 0.0)
    hum_cats = data.get("humanitarian_categories", [])
    hum_score = min(len([c for c in hum_cats if c != 'none']), 9) / 9.0 if isinstance(hum_cats, list) else 0.0

    return round(
        0.5 * seriousness +
        0.2 * informativeness +
        0.2 * damage +
        0.1 * hum_score,
        4
    )

def upsert_aggregate(location, new_score, disaster_type):
    # Get current
    res = supabase.table(agg_table).select("id, aggregate_score, tweet_count").eq("location", location).execute()
    if res.data:
        row = res.data[0]
        count = row.get("tweet_count", 1)
        prev_score = row.get("aggregate_score", 0)
        new_count = count + 1
        running_avg = (prev_score * count + new_score) / new_count
        supabase.table(agg_table).update({
            "aggregate_score": running_avg,
            "tweet_count": new_count,
            "disaster_type": disaster_type  # update to most recent
        }).eq("location", location).execute()
        return running_avg, new_count, disaster_type
    else:
        supabase.table(agg_table).insert({
            "location": location,
            "disaster_type": disaster_type,
            "aggregate_score": new_score,
            "tweet_count": 1
        }).execute()
        return new_score, 1, disaster_type

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

            location = data.get("location")
            disaster_type = data.get("disaster_type")
            if not location:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing location"}).encode())
                return

            agg_score = calc_aggregate_score(data)
            avg, count, dtype = upsert_aggregate(location, agg_score, disaster_type)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "location": location,
                "disaster_type": dtype,
                "aggregate_score": avg,
                "tweet_count": count
            }).encode())
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