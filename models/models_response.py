"""
Created on 2025.02.27

@Title: OroraTech Wildfire Tech Challenge - models
@author: jseelig

This script contains models for typed response
"""

from pydantic import BaseModel
from typing import List


class Properties(BaseModel):
    """Base properties part of the response"""

    # id: Optional[int] = None
    # latitude: Optional[float] = Field(
    #     None, ge=-90, le=90, description="Latitude (-90 to 90)"
    # )
    # longitude: Optional[float] = Field(
    #     None, ge=-180, le=180, description="Longitude (-180 to 180)"
    # )
    # timestamp_start: Optional[datetime] = None
    # timestamp_end: Optional[datetime] = None
    # error: Optional[str] = None  # Adding error message field
    # model_config = {"extra": "ignore"}  # If detection has params unknown to Properties


class FeatGeometry(BaseModel):
    """Geometries for Spatial List part of the response"""

    type: str
    coordinates: List[float]


class Feature(BaseModel):
    """Features for List part of the response"""

    type: str
    geometry: FeatGeometry
    properties: Properties


class SpatialGeoJsonResponse(BaseModel):
    """Base Model for typed response for search-by-Spatial"""

    type: str
    features: List[Feature]
