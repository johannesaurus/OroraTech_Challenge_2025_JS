"""
Created on 27.02.2025

@Title: OroraTech Wildfire Tech Challenge - mockDB
@author: jseelig

This script calls and holds mock DB data
"""

from shapely.geometry import Point
import os
import csv
from datetime import datetime

import settings
import csv_fcts
from models import HotspotEntry
from typing import Dict, Optional

# Initialize data store
data: Dict[int, HotspotEntry] = {}

# Load data from CSV
if not os.path.exists(settings.MASTER_CSV):
    data = csv_fcts.read_csv_files(settings.CHALLENGE_CSV_DIR)
    csv_fcts.write_mockdb_to_mastercsv(data)
else:
    data = csv_fcts.read_mastercsv_to_dict()


def get_hotspot(id: int) -> Optional[HotspotEntry]:
    """Returns a hotspot based on ID."""
    return data.get(id)


def add_hotspot(
    id: int, latitude: float, longitude: float, timestamp_start: str, timestamp_end: str
) -> None:
    """Appends a new hotspot entry to the CSV file."""
    hotspot = HotspotEntry(
        id=id,
        latitude=latitude,
        longitude=longitude,
        timestamp_start=datetime.strptime(timestamp_start, "%Y-%m-%d %H:%M:%S"),
        timestamp_end=datetime.strptime(timestamp_end, "%Y-%m-%d %H:%M:%S"),
        geom=Point(longitude, latitude),
    )
    data[id] = hotspot  # Add to in-memory data store

    # Append to CSV
    with open(settings.MASTER_CSV, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=settings.CSV_FIELDS)
        writer.writerow(hotspot.dict())


def delete_hotspot(id: int) -> bool:
    """Deletes a hotspot entry by ID from the data store and CSV file."""
    if id not in data:
        return False

    del data[id]
    csv_fcts.write_mockdb_to_mastercsv(data)  # Rewrite CSV without deleted entry
    return True


def get_next_hotspot_id() -> int:
    """Retrieve the next available hotspot ID (highest ID + 1)."""
    return max(data.keys(), default=0) + 1
