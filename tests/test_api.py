import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from models.models_db import Base, FireDetection
from api.api import app, get_db

# Create a test database in memory
test_engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Setup test database
Base.metadata.create_all(bind=test_engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# Override the dependency
def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "In Root"}

def test_add_hotspot(db_session):
    response = client.post(
        "/hotspots/add",
        params={
            "latitude": 34.5,
            "longitude": -117.3,
            "timestamp_start": datetime.utcnow().isoformat(),
            "timestamp_end": datetime.utcnow().isoformat(),
        },
    )
    assert response.status_code == 200
    assert "Hotspot with ID" in response.json()["message"]

def test_get_hotspots_empty():
    response = client.get("/hotspots")
    assert response.status_code == 404
    assert response.json()["detail"] == "No hotspots found"

def test_delete_hotspot_not_found():
    response = client.delete("/hotspots/remove", params={"id": 999})
    assert response.status_code == 404
    assert response.json()["detail"] == "Hotspot not found"

def test_validate_polygon_invalid():
    invalid_polygons = [
        "not a json",
        json.dumps({"wrong_key": []}),
        json.dumps({"coordinates": []}),
    ]
    for polygon in invalid_polygons:
        response = client.get("/hotspots", params={"polygon": polygon})
        assert response.status_code == 400
        assert "Invalid polygon format" in response.json()["detail"]

def test_get_hotspot_by_id_not_found():
    response = client.get("/hotspots/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Hotspot not found"

def test_get_hotspot_by_id(db_session):
    hotspot = FireDetection(latitude=34.5, longitude=-117.3, timestamp_start=datetime.utcnow(), timestamp_end=datetime.utcnow())
    db_session.add(hotspot)
    db_session.commit()
    db_session.refresh(hotspot)

    response = client.get(f"/hotspots/{hotspot.id}")
    assert response.status_code == 200
    assert response.json()["geometry"]["coordinates"] == [hotspot.longitude, hotspot.latitude]

def test_delete_hotspot_success(db_session):
    hotspot = FireDetection(latitude=34.5, longitude=-117.3, timestamp_start=datetime.utcnow(), timestamp_end=datetime.utcnow())
    db_session.add(hotspot)
    db_session.commit()
    db_session.refresh(hotspot)

    response = client.delete("/hotspots/remove", params={"id": hotspot.id})
    assert response.status_code == 200
    assert response.json()["message"] == f"Hotspot with ID {hotspot.id} deleted successfully"
    