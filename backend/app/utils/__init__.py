"""
===============================================================================
WildLink AI — Utilities Package (GeoJSON & Response Formatters)
===============================================================================
Provides helper functions for GIS GeoJSON construction and standard API responses:
- success_response / error_response — Standard API response dictionaries
- geojson_point                     — GeoJSON Point object constructor
- geojson_polygon                   — GeoJSON Polygon object constructor
- geojson_feature                   — GeoJSON Feature wrapper
- geojson_feature_collection        — GeoJSON FeatureCollection wrapper
"""

__title__ = "WildLink Utilities Package"
__description__ = "GeoJSON serialization helpers and API response formatters"

from app.utils.geo_helpers import (
    success_response,
    error_response,
    geojson_point,
    geojson_polygon,
    geojson_feature,
    geojson_feature_collection,
)

__all__ = [
    "success_response",
    "error_response",
    "geojson_point",
    "geojson_polygon",
    "geojson_feature",
    "geojson_feature_collection",
]
