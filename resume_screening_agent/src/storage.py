"""
STEP 5 (optional save step): persists screening results to JSON and CSV
so a reviewer can inspect a full run without re-calling the API.
"""

import csv
import json
import os
from datetime import datetime

from src.config import RESULTS_DIR


def save_results(results: list, tag: str = "run") -> tuple:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = os.path.join(RESULTS_DIR, f"{tag}_{timestamp}.json")
    csv_path = os.path.join(RESULTS_DIR, f"{tag}_{timestamp}.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    if results:
        fieldnames = list(results[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                row_copy = row.copy()
                for key in ("matched_skills", "missing_skills", "strengths", "concerns"):
                    if key in row_copy and isinstance(row_copy[key], list):
                        row_copy[key] = "; ".join(row_copy[key])
                writer.writerow(row_copy)

    return json_path, csv_path
