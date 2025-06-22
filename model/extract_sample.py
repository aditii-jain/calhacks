import csv

CSV_PATH = "model/sample/california_fires/metadata.csv"

with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader):
        if idx >= 2:
            break
        tweet_text = row.get("tweet_text")
        image_url = row.get("image_url")
        print({"tweet_text": tweet_text, "image_url": image_url})
