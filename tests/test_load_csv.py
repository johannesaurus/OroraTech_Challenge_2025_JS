import pytest
import os
import csv
import re
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models_db import Base, FireDetection, SessionLocal
from fcts.load_csv import extract_relevant_data, extract_timestamps_from_filename, load_csv_to_db

# Create a test database in memory
test_engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_extract_relevant_data():
    row1 = {"lat": "45.0", "lon": "-120.0"}
    row2 = {"latitude": "50.5", "longitude": "-130.5"}
    row3 = {"x": "100", "y": "200"}  # No lat/lon fields

    assert extract_relevant_data(row1) == (45.0, -120.0)
    assert extract_relevant_data(row2) == (50.5, -130.5)
    assert extract_relevant_data(row3) == (None, None)

def test_extract_timestamps_from_filename():
    filename = "2025-03-03T123456.789Z_2025-03-03T223456.789Z_data.csv"
    timestamp_start, timestamp_end = extract_timestamps_from_filename(filename)
    assert timestamp_start == datetime.strptime("2025-03-03T123456.789Z", "%Y-%m-%dT%H%M%S.%fZ")
    assert timestamp_end == datetime.strptime("2025-03-03T223456.789Z", "%Y-%m-%dT%H%M%S.%fZ")

def test_extract_timestamps_invalid():
    filename = "invalid_filename.csv"
    timestamp_start, timestamp_end = extract_timestamps_from_filename(filename)
    assert timestamp_start is None
    assert timestamp_end is None

def test_load_csv_to_db(mocker, db_session):
    mocker.patch("load_csv.DATA_DIR", new="test_data")
    os.makedirs("test_data", exist_ok=True)
    csv_content = "lat,lon\n34.5,-117.3\n35.1,-118.2\n"
    
    with open("test_data/test_2025-03-03T123456.789Z_2025-03-03T223456.789Z.csv", "w") as f:
        f.write(csv_content)
    
    load_csv_to_db()
    
    results = db_session.query(FireDetection).all()
    assert len(results) == 2
    assert results[0].latitude == 34.5
    assert results[0].longitude == -117.3
    assert results[1].latitude == 35.1
    assert results[1].longitude == -118.2
    
    os.remove("test_data/test_2025-03-03T123456.789Z_2025-03-03T223456.789Z.csv")
    os.rmdir("test_data")