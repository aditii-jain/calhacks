import os
import csv
import requests
from classification import classify_crisismmd
from PIL import Image

CSV_PATH = "model/sample/california_fires/metadata.csv"
SAMPLE_DIR = "model/sample/california_fires"
RESULTS_PATH = "model/sample/california_fires/classification_results.json"

# Number of rows to process
N_ROWS = 10  # Change this to set how many rows to process

# Columns to compare for confidence scores
CONF_COLUMNS = [
    "text_info_conf",
    "image_info_conf",
    "text_human_conf",
    "image_human_conf",
    "image_damage_conf"
]

# Function to compare actual vs predicted confidence scores
def compare_scores(row, result):
    diffs = []
    for col in CONF_COLUMNS:
        actual = row.get(col)
        predicted = result.get(col)
        try:
            actual_val = float(actual) if actual not in (None, "") else None
            predicted_val = float(predicted) if predicted not in (None, "") else None
        except Exception:
            actual_val, predicted_val = actual, predicted
        if actual_val != predicted_val:
            diffs.append(f"{col}: actual={actual_val}, predicted={predicted_val}")
    return diffs

def download_image(url, dest_path):
    if os.path.exists(dest_path):
        return
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(resp.content)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    results = []
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            if idx >= N_ROWS:
                break  # Only process up to N_ROWS rows
            image_url = row["image_url"]
            image_id = row["image_id"]
            tweet_text = row["tweet_text"]
            print(f"Processing {idx+1}/{N_ROWS}: tweet_id={row['tweet_id']}, image_id={image_id}")
            # Save image
            image_ext = os.path.splitext(image_url)[1].split("?")[0] or ".jpg"
            image_filename = f"{image_id}{image_ext}"
            image_path = os.path.join(SAMPLE_DIR, image_filename)
            download_image(image_url, image_path)
            if not os.path.exists(image_path):
                print(f"Image file does not exist, skipping {image_id}")
                continue
            try:
                result = classify_crisismmd(tweet_text, image_path)
                # Compare confidence scores
                diffs = compare_scores(row, result)
                if diffs:
                    print(f"Differences for tweet_id={row['tweet_id']}, image_id={image_id}:")
                    for d in diffs:
                        print("  " + d)
                else:
                    print(f"No differences for tweet_id={row['tweet_id']}, image_id={image_id}")
                # Store result
                result["tweet_id"] = row["tweet_id"]
                result["image_id"] = image_id
                results.append(result)
                print(f"Classified {image_id}")
            except Exception as e:
                print(f"Classification failed for {image_id}: {e}")
                continue

    # Save results
    import json
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    try:
        main()
        print(f"Finished processing up to {N_ROWS} rows.")
    except Exception as e:
        print(f"Error during processing: {e}")