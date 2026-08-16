"""
WildLink AI — Utility Helpers
"""
from typing import Any, Dict, Optional
from app.schemas import ApiResponse, ApiError


def success_response(data: Any = None, message: str = "Success") -> dict:
    """Create a standard success response."""
    return {
        "success": True,
        "data": data,
        "message": message
    }


def error_response(code: str, message: str) -> dict:
    """Create a standard error response."""
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }


def geojson_point(lat: float, lng: float) -> dict:
    """Create a GeoJSON Point geometry."""
    return {
        "type": "Point",
        "coordinates": [lng, lat]
    }


def geojson_polygon(coordinates: list) -> dict:
    """Create a GeoJSON Polygon geometry."""
    return {
        "type": "Polygon",
        "coordinates": coordinates
    }


def geojson_feature(geometry: dict, properties: dict = None) -> dict:
    """Create a GeoJSON Feature."""
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": properties or {}
    }


def geojson_feature_collection(features: list) -> dict:
    """Create a GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "features": features
    }
