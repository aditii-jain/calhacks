import base64
import requests
import random
import time
from datetime import datetime, timezone

# Path to your JPEG file
image_path = "model/sample/california_fires/917791044158185473_0.jpg"

# Read and encode image
with open(image_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
data_url = f"data:image/jpeg;base64,{b64}"

# Prepare payload
payload = {
    "image_data": data_url,
    "tweet_text": "Wildfires raging through San Francisco are crazy!!!!! There are so many people affected by this disaster!!! #CaliforniaFires",
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

# Send POST request
resp = requests.post(
    "https://calhack4.vercel.app/api/orchestrate",
    json=payload,
    timeout=60
)

print(resp.status_code)
print(resp.text)