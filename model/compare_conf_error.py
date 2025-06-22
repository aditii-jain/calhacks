"""
Standalone script to evaluate confidence prediction errors.

This script reads the ground-truth metadata CSV and the classification results JSON,
computes mean absolute error (MAE) for each confidence column and overall average error,
and prints an error report.
"""
import os
import csv
import json

# Paths to metadata and results
CSV_PATH = os.path.join(os.path.dirname(__file__), "sample", "california_fires", "metadata.csv")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "sample", "california_fires", "classification_results.json")

# Confidence columns to compare
CONF_COLUMNS = [
    "text_info_conf",
    "image_info_conf",
    "text_human_conf",
    "image_human_conf",
    "image_damage_conf"
]

def load_metadata(csv_path):
    """Load metadata CSV into dict keyed by (tweet_id, image_id)."""
    mapping = {}
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = (row['tweet_id'], row['image_id'])
            mapping[key] = row
    return mapping


def load_results(json_path):
    """Load classification results JSON into list of records."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_error(metadata, results):
    """Compute MAE per column and overall MAE."""
    errors = {col: 0.0 for col in CONF_COLUMNS}
    counts = {col: 0 for col in CONF_COLUMNS}
    total_error = 0.0
    total_count = 0

    for rec in results:
        key = (rec.get('tweet_id'), rec.get('image_id'))
        actual_row = metadata.get(key)
        if not actual_row:
            print(f"Warning: no metadata for {key}, skipping.")
            continue
        for col in CONF_COLUMNS:
            actual_val = actual_row.get(col)
            pred_val = rec.get(col)
            try:
                a = float(actual_val)
                p = float(pred_val)
                err = abs(a - p)
                errors[col] += err
                counts[col] += 1
                total_error += err
                total_count += 1
            except Exception:
                # skip if missing or non-numeric
                continue

    mae = {col: (errors[col] / counts[col] if counts[col] else None) for col in CONF_COLUMNS}
    overall_mae = (total_error / total_count) if total_count else None
    return mae, overall_mae, counts


def main():
    metadata = load_metadata(CSV_PATH)
    results = load_results(RESULTS_PATH)

    mae, overall_mae, counts = compute_error(metadata, results)

    print("Confidence Error Report:")
    for col in CONF_COLUMNS:
        if counts[col]:
            print(f"  {col}: MAE = {mae[col]:.4f} over {counts[col]} samples")
        else:
            print(f"  {col}: no valid samples to compute error")
    if overall_mae is not None:
        print(f"Overall MAE across all columns and rows: {overall_mae:.4f}")
    else:
        print("No valid comparisons found.")

if __name__ == '__main__':
    main()
