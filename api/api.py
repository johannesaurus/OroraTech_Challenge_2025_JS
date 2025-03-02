"""
Created on 27.02.2025

@Title: OroraTech Wildfire Tech Challenge - api
@author: jseelig

This script contains api calls
"""

from fastapi import FastAPI, Query, HTTPException
from shapely.geometry import Polygon, Point
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple, cast

import fcts.mock_db as mock_db
from models.models_response import (
    IDGeoJsonResponse,
    SpatialGeoJsonResponse,
    Properties,
    FeatGeometry
)
from models.models_entry import HotspotEntry

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "In Root"}


def validate_polygon(polygon: str) -> Polygon:
    """Validate and parse the polygon input."""
    try:
        geojson: Dict[str, Any] = json.loads(polygon)
        coords: Optional[List[List[List[float]]]] = geojson.get("coordinates")
        if not coords:
            raise ValueError("No coordinates found in the polygon")
        return Polygon(coords[0])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid polygon format: {str(e)}")


def is_within_timestamp_range(
    detection: Dict[str, Any],
    start_timestamp: Optional[datetime],
    end_timestamp: Optional[datetime],
) -> bool:
    """Compare detection timestamps with user-specified range."""
    if start_timestamp and end_timestamp:
        detection_start: datetime = datetime.fromisoformat(detection["timestamp_start"])
        detection_end: datetime = datetime.fromisoformat(detection["timestamp_end"])
        return (
            start_timestamp <= detection_start <= end_timestamp
            or start_timestamp <= detection_end <= end_timestamp
        )
    return True  # No filtering by default


def convert_point_to_geometry(point: Point) -> FeatGeometry:
    return FeatGeometry(type="Point", coordinates=[[point.x, point.y]])


def convert_geometry_to_point(geometry: FeatGeometry) -> Point:
    """Convert a FeatGeometry object to a Point."""
    # Assuming the coordinates are in the format: [[longitude, latitude]]
    longitude, latitude = geometry.coordinates[0]
    return Point(longitude, latitude)


async def get_db() -> None:
    """
    Dependency for database session (for compatibility, though mock_db doesn't need it)
    Mock DB does not require a session
    """
    return None


@app.get("/hotspots", response_model=SpatialGeoJsonResponse)
async def get_hotspots(
    polygon: Optional[str] = Query(
        None, description="GeoJSON Polygon geometry as a string"
    ),
    min_lat: Optional[float] = Query(
        None, description="Minimum latitude (for bounding box)"
    ),
    max_lat: Optional[float] = Query(
        None, description="Maximum latitude (for bounding box)"
    ),
    min_lon: Optional[float] = Query(
        None, description="Minimum longitude (for bounding box)"
    ),
    max_lon: Optional[float] = Query(
        None, description="Maximum longitude (for bounding box)"
    ),
    start_timestamp: Optional[datetime] = Query(
        None, description="Filter by start timestamp (ISO format)"
    ),
    end_timestamp: Optional[datetime] = Query(
        None, description="Filter by end timestamp (ISO format)"
    ),
) -> SpatialGeoJsonResponse:
    """
    Endpoint to get fire detections within a polygon/bounding box + opt:Timestamp
    The user should send polygon as GeoJSON polygon format
    OR Convert bounding box: shapely geometry to GeoJSON
    """
    if polygon:
        query_shape: Polygon = validate_polygon(polygon)
    elif all(param is not None for param in [min_lat, max_lat, min_lon, max_lon]):
        coordinates: List[Tuple[float, float]] = [
            (cast(float, min_lon), cast(float, min_lat)),
            (cast(float, min_lon), cast(float, max_lat)),
            (cast(float, max_lon), cast(float, max_lat)),
            (cast(float, max_lon), cast(float, min_lat)),
            (cast(float, min_lon), cast(float, min_lat)),
        ]

        query_shape = Polygon(coordinates)
    else:
        query_shape = Polygon()
        raise HTTPException(
            status_code=400,
            detail="You must provide either a polygon or bounding box parameters.",
        )

    filtered_detections: List[Dict[str, Any]] = [
        detection
        for detection in mock_db.data.values()
        if query_shape.contains(convert_geometry_to_point(detection["geom"]))
        and is_within_timestamp_range(
            detection if isinstance(detection, HotspotEntry) else detection,
            start_timestamp,
            end_timestamp,
        )
    ]

    if not filtered_detections:
        raise HTTPException(status_code=404, detail="No hotspots found")

    features: List[Dict[str, Any]] = [
        {
            "type": "Feature",
            "geometry": detection["geom"],
            #"properties": Properties(**detection),
        }
        for detection in filtered_detections
    ]

    return SpatialGeoJsonResponse(type="FeatureCollection", features=features)
    # feature_dicts = [
    #     {
    #         "type": "Feature",  # Assuming you want to label all as "Feature"
    #         "geometry": detection.get("geometry"),  # Adjust according to actual field names
    #         "properties": {
    #             "id": detection.get("id"),
    #             "latitude": detection.get("latitude"),
    #             "longitude": detection.get("longitude"),
    #             # Add other properties as necessary
    #         },
    #     }
    #     for detection in filtered_detections
    # ]
    # features = [Feature(**feature_dict) for feature_dict in feature_dicts]
    # return SpatialGeoJsonResponse(type="FeatureCollection", features=features)


@app.get("/hotspots/{id}", response_model=IDGeoJsonResponse)
async def get_hotspot_by_id(id: int) -> IDGeoJsonResponse:
    """Retrieve a fire detection by ID."""
    detection: Optional[Dict[str, Any]] = mock_db.get_hotspot(id)
    result = (
        mock_db.get_hotspot(id).model_dump()
        if mock_db.get_hotspot(id) is not None
        else None
    )  # Convert to dict if not None

    if not detection:
        raise HTTPException(status_code=404, detail="Hotspot not found")
    return IDGeoJsonResponse(
        type="Feature", geometry=detection["geom"]#, properties=Properties(**detection)
    )


@app.post("/hotspots/add", response_model=Dict[str, str])
async def add_new_hotspot(
    latitude: float,
    longitude: float,
    timestamp_start: datetime,
    timestamp_end: datetime,
) -> Dict[str, str]:
    """Endpoint to add a fire detection"""
    new_id: int = mock_db.get_next_hotspot_id()
    mock_db.add_hotspot(
        new_id,
        latitude,
        longitude,
        timestamp_start.isoformat(),
        timestamp_end.isoformat(),
    )
    return {"message": f"Hotspot with ID {new_id} added successfully"}


@app.delete("/hotspots/remove", response_model=Dict[str, str])
async def delete_hotspot_by_id(
    id: int = Query(..., description="ID of the hotspot to remove"),
) -> Dict[str, str]:
    """Delete a fire detection by ID."""
    mock_db.delete_hotspot(id)
    return {"message": f"Hotspot with ID {id} deleted successfully"}
