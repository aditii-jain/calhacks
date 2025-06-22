import os
import csv
from classification import classify_crisismmd

CSV_PATH = "model/sample/california_fires/metadata.csv"
SAMPLE_DIR = "model/sample/california_fires"
N_ROWS = 2  # Change this to set how many rows to process

CONF_COLUMNS = [
    "text_info_conf",
    "image_info_conf",
    "text_human_conf",
    "image_human_conf",
    "image_damage_conf"
]

def download_image(url, dest_path):
    if os.path.exists(dest_path):
        return
    import requests
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(resp.content)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            if idx >= N_ROWS:
                break
            image_url = row["image_url"]
            image_id = row["image_id"]
            tweet_text = row["tweet_text"]
            print(f"Processing {idx+1}/{N_ROWS}: tweet_id={row['tweet_id']}, image_id={image_id}")
            image_ext = os.path.splitext(image_url)[1].split("?")[0] or ".jpg"
            image_filename = f"{image_id}{image_ext}"
            image_path = os.path.join(SAMPLE_DIR, image_filename)
            download_image(image_url, image_path)
            if not os.path.exists(image_path):
                print(f"Image file does not exist, skipping classification for {image_id}: {image_path}")
                print(f"Skipped {image_id} due to missing image.")
                continue
            try:
                result = classify_crisismmd(tweet_text, image_path)
                print(f"Classified tweet_id={row['tweet_id']}, image_id={image_id}")
            except Exception as e:
                print(f"Classification failed for {image_id}: {e}")
                continue

if __name__ == "__main__":
    main()