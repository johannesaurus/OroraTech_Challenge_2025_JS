import csv
import os
import sys

import re
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.models_db import SessionLocal, FireDetection, init_db

init_db()

DATA_DIR = r"C:\Users\jseelig\Desktop\side_projects\OroraTech_1\OroraTech_Challenge_2025_JS\data"


def extract_relevant_data(row):
    """Extract latitude and longitude from different CSV column formats."""
    possible_lat_keys = ["lat", "latitude"]
    possible_lon_keys = ["lon", "longitude"]

    lat = next(
        (float(row[key]) for key in possible_lat_keys if key in row and row[key]), None
    )
    lon = next(
        (float(row[key]) for key in possible_lon_keys if key in row and row[key]), None
    )

    return lat, lon


def extract_timestamps_from_filename(filename):
    """Extract timestamp_start and timestamp_end from the filename."""
    match = re.search(
        r"(\d{4}-\d{2}-\d{2}T\d{6}\.\d+Z)_(\d{4}-\d{2}-\d{2}T\d{6}\.\d+Z)", filename
    )
    if match:
        timestamp_start = datetime.strptime(match.group(1), "%Y-%m-%dT%H%M%S.%fZ")
        timestamp_end = datetime.strptime(match.group(2), "%Y-%m-%dT%H%M%S.%fZ")
        return timestamp_start, timestamp_end
    return None, None


def load_csv_to_db():
    db: Session = SessionLocal()
    for file_name in os.listdir(DATA_DIR):
        if file_name.endswith(".csv"):
            file_path = os.path.join(DATA_DIR, file_name)
            print(f"Processing: {file_path}")

            timestamp_start, timestamp_end = extract_timestamps_from_filename(file_name)
            if not timestamp_start or not timestamp_end:
                print(f"Skipping {file_name}: Unable to extract timestamps.")
                continue

            with open(file_path, newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    lat, lon = extract_relevant_data(row)
                    if lat is not None and lon is not None:
                        fire = FireDetection(
                            latitude=lat,
                            longitude=lon,
                            timestamp_start=timestamp_start,
                            timestamp_end=timestamp_end,
                        )
                        db.add(fire)
    db.commit()
    db.close()
    print("Data ingestion completed.")


if __name__ == "__main__":
    load_csv_to_db()
