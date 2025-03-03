"""
Created on 2025.02.27
Edited on 2025.03.03

@Title: OroraTech Wildfire Tech Challenge - api
@author: jseelig

This script contains api calls
"""
from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from shapely.geometry import Polygon, Point
from sqlalchemy import or_

import json
from datetime import datetime
from typing import Optional

from models.model_db import SessionLocal, FireDetection
from models.models_response import SpatialGeoJsonResponse, FeatGeometry,Feature

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "In Root"}

def validate_polygon(polygon: str) -> Polygon:
    try:
        geojson = json.loads(polygon)
        coords = geojson.get("coordinates")
        if not coords:
            raise ValueError("No coordinates found in the polygon")
        return Polygon(coords[0])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid polygon format: {str(e)}")

@app.get("/hotspots", response_model=SpatialGeoJsonResponse)
def get_hotspots(
    db: Session = Depends(get_db),
    polygon: Optional[str] = Query(None, description="GeoJSON Polygon geometry as a string"),
    min_lat: Optional[float] = Query(None, description="Minimum latitude"),
    max_lat: Optional[float] = Query(None, description="Maximum latitude"),
    min_lon: Optional[float] = Query(None, description="Minimum longitude"),
    max_lon: Optional[float] = Query(None, description="Maximum longitude"),
    start_timestamp: Optional[datetime] = Query(None, description="Filter by start timestamp"),
    end_timestamp: Optional[datetime] = Query(None, description="Filter by end timestamp"),
):
    query = db.query(FireDetection)

    if start_timestamp and end_timestamp:
        query = query.filter(
            or_(
                FireDetection.timestamp_start.between(start_timestamp, end_timestamp),
                FireDetection.timestamp_end.between(start_timestamp, end_timestamp)
            )
        )

    if all(param is not None for param in [min_lat, max_lat, min_lon, max_lon]):
        query = query.filter(FireDetection.latitude.between(min_lat, max_lat), FireDetection.longitude.between(min_lon, max_lon))
    
    detections = query.all()
    
    if polygon:
        polygon_shape = validate_polygon(polygon)
        detections = [d for d in detections if polygon_shape.contains(Point(d.longitude, d.latitude))]
    
    if not detections:
        raise HTTPException(status_code=404, detail="No hotspots found")
    
    features = [{
        "type": "Feature",
        "geometry": FeatGeometry(type="Point", coordinates=[d.longitude, d.latitude]),
        "properties": {}
    } for d in detections]
    return SpatialGeoJsonResponse(type="FeatureCollection", features=features)

@app.get("/hotspots/{id}", response_model=Feature)
def get_hotspot_by_id(id: int, db: Session = Depends(get_db)):
    detection = db.query(FireDetection).filter(FireDetection.id == id).first()
    if not detection:
        raise HTTPException(status_code=404, detail="Hotspot not found")
    return Feature(
        type="Feature",
        geometry=FeatGeometry(type="Point", coordinates=[detection.longitude, detection.latitude]),
        properties={}
    )

@app.post("/hotspots/add")
def add_new_hotspot(
    latitude: float,
    longitude: float,
    timestamp_start: datetime,
    timestamp_end: datetime,
    db: Session = Depends(get_db)
):
    new_fire = FireDetection(latitude=latitude, longitude=longitude, timestamp_start=timestamp_start, timestamp_end=timestamp_end)
    db.add(new_fire)
    db.commit()
    db.refresh(new_fire)
    return {"message": f"Hotspot with ID {new_fire.id} added successfully"}

@app.delete("/hotspots/remove")
def delete_hotspot_by_id(id: int, db: Session = Depends(get_db)):
    detection = db.query(FireDetection).filter(FireDetection.id == id).first()
    if not detection:
        raise HTTPException(status_code=404, detail="Hotspot not found")
    db.delete(detection)
    db.commit()
    return {"message": f"Hotspot with ID {id} deleted successfully"}

