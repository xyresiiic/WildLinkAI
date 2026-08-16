"""
===============================================================================
WildLink AI — Schemas Package (Pydantic Request & Response DTOs)
===============================================================================
Defines strict Pydantic v2 data validation schemas for all REST API endpoints:
- User & Auth: UserCreate, UserLogin, UserResponse, TokenResponse
- Species: SpeciesCreate, SpeciesResponse
- Projects: ProjectCreate, ProjectResponse, ProjectDetail, DashboardStats
- Spatial Layers: ObservationResponse, HabitatZoneResponse, CorridorResponse, PriorityZoneResponse
- Simulations: SimulationCreate, SimulationResponse, ScenarioComparison
- GeoJSON: GeoJSONFeature, GeoJSONFeatureCollection
- Wrappers: ApiResponse, ApiError
"""

__title__ = "WildLink Validation Schemas Package"
__description__ = "Pydantic v2 validation contracts and API data transfer objects"

from app.schemas.conservation_schemas import (
    ApiResponse,
    ApiError,
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    SpeciesCreate,
    SpeciesResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectDetail,
    ObservationCreate,
    ObservationResponse,
    AnalysisRequest,
    AnalysisJobResponse,
    HabitatZoneResponse,
    CorridorResponse,
    PriorityZoneResponse,
    SimulationCreate,
    SimulationResponse,
    ScenarioComparison,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    DashboardStats,
)

__all__ = [
    "ApiResponse",
    "ApiError",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "SpeciesCreate",
    "SpeciesResponse",
    "ProjectCreate",
    "ProjectResponse",
    "ProjectDetail",
    "ObservationCreate",
    "ObservationResponse",
    "AnalysisRequest",
    "AnalysisJobResponse",
    "HabitatZoneResponse",
    "CorridorResponse",
    "PriorityZoneResponse",
    "SimulationCreate",
    "SimulationResponse",
    "ScenarioComparison",
    "GeoJSONFeature",
    "GeoJSONFeatureCollection",
    "DashboardStats",
]
