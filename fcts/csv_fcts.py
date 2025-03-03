"""
Created on 2025.02.27

@Title: OroraTech Wildfire Tech Challenge - csv fcts
@author: jseelig

This script contains fcts for csv (mockDB) handling
"""

import os
import csv
from datetime import datetime

import settings
from models.models_response import FeatGeometry
from typing import Dict


def read_csv_files(directory: str) -> Dict:
    """Read data from provided csv files"""
    print("Importing from provided csvs")
    data = {}
    id_counter = 1
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            parts = filename.split("_")
            time_ctr = 0
            for i,part in enumerate(parts):
                if part.endswith('Z') and '.' in part:
                    time_ctr = i
                    break
            if time_ctr is not None and time_ctr + 1 < len(parts):
                timestamp_start = parts[time_ctr]
                timestamp_end = parts[time_ctr+1]
            else:
                print(f"Skipping file (invalid format): {filename}")
            filepath = os.path.join(directory, filename)
            with open(filepath, mode="r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    latitude = float(row["lat"])
                    longitude = float(row["lon"])
                    geom = FeatGeometry(type="Point", coordinates=[longitude, latitude])

                    data[id_counter] = {
                        "id": id_counter,
                        "latitude": latitude,
                        "longitude": longitude,
                        "timestamp_start": datetime.fromisoformat(
                            timestamp_start.rstrip("Z")
                        ),
                        "timestamp_end": datetime.fromisoformat(
                            timestamp_end.rstrip("Z")
                        ),
                        "geom": geom,
                    }
                    id_counter += 1
    return data


def write_mockdb_to_mastercsv(data: Dict) -> None:
    """Writes mock_db data to a master CSV file."""
    print("Importing DB from master csv")
    with open(settings.MASTER_CSV, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=settings.CSV_FIELDS)
        writer.writeheader()
        for record in data.values():
            writer.writerow(
                {
                    "id": record["id"],
                    "latitude": record["latitude"],
                    "longitude": record["longitude"],
                    "timestamp_start": record["timestamp_start"].isoformat(
                        timespec="microseconds"
                    )
                    + "Z",
                    "timestamp_end": record["timestamp_end"].isoformat(
                        timespec="microseconds"
                    )
                    + "Z",
                }
            )


def read_mastercsv_to_dict() -> Dict:
    """Reads the master CSV file into a dictionary."""
    data = {}
    if os.path.exists(settings.MASTER_CSV):
        with open(settings.MASTER_CSV, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:  # Skip empty rows
                    continue
                id_ = int(row["id"])
                geom = FeatGeometry(
                    type="Point",
                    coordinates=[float(row["longitude"]), float(row["latitude"])],
                )

                data[id_] = {
                    "id": id_,
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "timestamp_start": datetime.fromisoformat(
                        row["timestamp_start"].split("Z")[0]
                    ),
                    "timestamp_end": datetime.fromisoformat(
                        row["timestamp_end"].split("Z")[0]
                    ),
                    "geom": geom,
                }
    return data
