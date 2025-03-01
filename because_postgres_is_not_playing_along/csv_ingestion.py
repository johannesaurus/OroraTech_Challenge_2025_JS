import pandas as pd
import asyncio
import re

# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
from app.database import SessionLocal  # , engine
from app.models import FireDetection
from geoalchemy2.shape import from_shape
from shapely.geometry import Point


# Extract timestamp from filename
def extract_timestamp(filename: str):
    match = re.search(r"acquisition_(\d+)_", filename)
    return match.group(1) if match else None


# Function to insert data
async def insert_fire_detections(filename: str):
    df = pd.read_csv(filename, usecols=["lat", "lon"])  # Only keep relevant columns
    timestamp = extract_timestamp(filename)

    if not timestamp:
        print(f"Skipping {filename}: No valid timestamp found.")
        return

    async with SessionLocal() as session:
        for _, row in df.iterrows():
            fire_detection = FireDetection(
                latitude=row["lat"],
                longitude=row["lon"],
                timestamp=pd.to_datetime(timestamp, format="%Y%m%d%H%M%S"),
                geom=from_shape(
                    Point(row["lon"], row["lat"]), srid=4326
                ),  # Store as PostGIS Point
            )
            session.add(fire_detection)

        await session.commit()
        print(f"Ingested {len(df)} records from {filename}")


# Run ingestion for multiple files
async def main():
    files = [
        "F002_L2_FIRE____acquisition_20240201_120000.csv"
    ]  # Add all CSV filenames here
    await asyncio.gather(*(insert_fire_detections(file) for file in files))


if __name__ == "__main__":
    asyncio.run(main())
