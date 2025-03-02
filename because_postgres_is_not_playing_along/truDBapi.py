"""
Created on 27.02.2025

@Title: OroraTech Wildfire Tech Challenge - API
@author: jseelig

This script contains API calls with PostgreSQL + PostGIS integration.
"""

from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from shapely.geometry import Polygon
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple, cast

from models.models_response import (
    IDGeoJsonResponse,
    SpatialGeoJsonResponse,
    Properties,
    FeatGeometry,
    Feature,
    HotspotEntry,
)

from database import get_db, Hotspot

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


async def get_hotspots_from_db(
    db: AsyncSession,
    query_shape: Polygon,
    start_timestamp: Optional[datetime],
    end_timestamp: Optional[datetime],
) -> List[HotspotEntry]:
    """Fetch hotspots from the database within a given polygon and time range."""
    stmt = select(Hotspot).where(
        Hotspot.geom.ST_Within(f"ST_GeomFromText('{query_shape.wkt}', 4326)")
    )

    if start_timestamp and end_timestamp:
        stmt = stmt.where(
            (Hotspot.timestamp_start >= start_timestamp)
            & (Hotspot.timestamp_end <= end_timestamp)
        )

    result = await db.execute(stmt)
    return result.scalars().all()


@app.get("/hotspots", response_model=SpatialGeoJsonResponse)
async def get_hotspots(
    polygon: Optional[str] = Query(
        None, description="GeoJSON Polygon geometry as a string"
    ),
    min_lat: Optional[float] = Query(
        None, description="Minimum latitude (bounding box)"
    ),
    max_lat: Optional[float] = Query(
        None, description="Maximum latitude (bounding box)"
    ),
    min_lon: Optional[float] = Query(
        None, description="Minimum longitude (bounding box)"
    ),
    max_lon: Optional[float] = Query(
        None, description="Maximum longitude (bounding box)"
    ),
    start_timestamp: Optional[datetime] = Query(
        None, description="Start timestamp (ISO format)"
    ),
    end_timestamp: Optional[datetime] = Query(
        None, description="End timestamp (ISO format)"
    ),
    db: AsyncSession = Depends(get_db),
) -> SpatialGeoJsonResponse:
    """Get fire detections within a polygon/bounding box + optional timestamp filtering."""

    if polygon:
        query_shape = validate_polygon(polygon)
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
        raise HTTPException(
            status_code=400,
            detail="You must provide either a polygon or bounding box parameters.",
        )

    hotspots = await get_hotspots_from_db(
        db, query_shape, start_timestamp, end_timestamp
    )

    if not hotspots:
        raise HTTPException(status_code=404, detail="No hotspots found")

    features = [
        Feature(
            type="Feature",
            geometry=FeatGeometry(
                type="Point", coordinates=[[h.longitude, h.latitude]]
            ),
            properties=Properties(
                id=h.id,
                latitude=h.latitude,
                longitude=h.longitude,
                timestamp_start=h.timestamp_start,
                timestamp_end=h.timestamp_end,
            ),
        )
        for h in hotspots
    ]

    return SpatialGeoJsonResponse(type="FeatureCollection", features=features)


@app.get("/hotspots/{id}", response_model=IDGeoJsonResponse)
async def get_hotspot_by_id(
    id: int, db: AsyncSession = Depends(get_db)
) -> IDGeoJsonResponse:
    """Retrieve a fire detection by ID."""
    result = await db.execute(select(Hotspot).where(Hotspot.id == id))
    hotspot = result.scalar_one_or_none()

    if not hotspot:
        raise HTTPException(status_code=404, detail="Hotspot not found")

    return IDGeoJsonResponse(
        type="Feature",
        geometry=FeatGeometry(
            type="Point", coordinates=[[hotspot.longitude, hotspot.latitude]]
        ),
        properties=Properties(
            id=hotspot.id,
            latitude=hotspot.latitude,
            longitude=hotspot.longitude,
            timestamp_start=hotspot.timestamp_start,
            timestamp_end=hotspot.timestamp_end,
        ),
    )


@app.post("/hotspots/add", response_model=Dict[str, str])
async def add_new_hotspot(
    latitude: float,
    longitude: float,
    timestamp_start: datetime,
    timestamp_end: datetime,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Add a fire detection to the database."""
    new_hotspot = Hotspot(
        latitude=latitude,
        longitude=longitude,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        geom=f"POINT({longitude} {latitude})",
    )

    db.add(new_hotspot)
    await db.commit()
    await db.refresh(new_hotspot)

    return {"message": f"Hotspot with ID {new_hotspot.id} added successfully"}


@app.delete("/hotspots/remove", response_model=Dict[str, str])
async def delete_hotspot_by_id(
    id: int = Query(..., description="ID of the hotspot to remove"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Delete a fire detection by ID."""
    result = await db.execute(select(Hotspot).where(Hotspot.id == id))
    hotspot = result.scalar_one_or_none()

    if not hotspot:
        raise HTTPException(status_code=404, detail="Hotspot not found")

    await db.delete(hotspot)
    await db.commit()

    return {"message": f"Hotspot with ID {id} deleted successfully"}
