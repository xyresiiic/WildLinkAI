"""
WildLink AI — Pydantic Schemas

Request/response validation schemas for all API endpoints.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# ──────────────────────────── Enums ────────────────────────────

class ProjectStatusEnum(str, Enum):
    CREATED = "created"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatusEnum(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceQualityEnum(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


# ──────────────────────────── API Response Wrapper ────────────────────────────

class ApiResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None


class ApiError(BaseModel):
    """Standard API error response."""
    success: bool = False
    error: Dict[str, str]


# ──────────────────────────── Auth ────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ──────────────────────────── Species ────────────────────────────

class SpeciesResponse(BaseModel):
    id: str
    common_name: str
    scientific_name: str
    description: Optional[str] = None
    habitat_preferences: Optional[Dict[str, float]] = None
    conservation_status: Optional[str] = None
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class SpeciesCreate(BaseModel):
    common_name: str
    scientific_name: str
    description: Optional[str] = None
    habitat_preferences: Optional[Dict[str, float]] = None
    conservation_status: Optional[str] = None


# ──────────────────────────── Project ────────────────────────────

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    region_name: Optional[str] = None
    species_id: Optional[str] = None
    region_geojson: Optional[Dict[str, Any]] = None  # GeoJSON polygon


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    region_name: Optional[str] = None
    species_id: Optional[str] = None
    status: str
    created_at: datetime
    species: Optional[SpeciesResponse] = None

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectResponse):
    """Extended project response with analysis summaries."""
    habitat_zones_count: int = 0
    corridors_count: int = 0
    priority_zones_count: int = 0
    simulations_count: int = 0
    avg_habitat_score: Optional[float] = None
    avg_connectivity_score: Optional[float] = None
    region_geojson: Optional[Dict[str, Any]] = None


# ──────────────────────────── Observation ────────────────────────────

class ObservationResponse(BaseModel):
    id: str
    species_id: str
    latitude: float
    longitude: float
    observed_at: Optional[datetime] = None
    source: Optional[str] = None
    confidence: Optional[float] = None

    model_config = {"from_attributes": True}


class ObservationCreate(BaseModel):
    species_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    observed_at: Optional[datetime] = None
    source: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)


# ──────────────────────────── Analysis ────────────────────────────

class AnalysisRequest(BaseModel):
    project_id: str
    type: str = Field(..., pattern="^(habitat|fragmentation|connectivity|priority|full)$")
    parameters: Optional[Dict[str, Any]] = None


class AnalysisJobResponse(BaseModel):
    id: str
    project_id: str
    type: str
    status: str
    progress: int = 0
    error: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────── Habitat Zone ────────────────────────────

class HabitatZoneResponse(BaseModel):
    id: str
    project_id: str
    suitability_score: float
    area_hectares: Optional[float] = None
    patch_id: Optional[int] = None
    fragmentation_level: Optional[str] = None
    nearest_patch_distance_km: Optional[float] = None
    geometry_geojson: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


# ──────────────────────────── Corridor ────────────────────────────

class CorridorResponse(BaseModel):
    id: str
    project_id: str
    source_patch_id: Optional[int] = None
    target_patch_id: Optional[int] = None
    connectivity_score: Optional[float] = None
    resistance_score: Optional[float] = None
    length_km: Optional[float] = None
    geometry_geojson: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


# ──────────────────────────── Priority Zone ────────────────────────────

class PriorityZoneResponse(BaseModel):
    id: str
    project_id: str
    rank: Optional[int] = None
    priority_score: float
    priority_level: Optional[str] = None

    # Factor scores
    habitat_score: Optional[float] = None
    connectivity_score: Optional[float] = None
    species_score: Optional[float] = None
    restoration_score: Optional[float] = None

    # Explainability
    dominant_factor: Optional[str] = None
    explanation: Optional[str] = None
    evidence_quality: Optional[str] = None
    factors_json: Optional[Dict[str, Any]] = None

    area_hectares: Optional[float] = None
    geometry_geojson: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


# ──────────────────────────── Simulation ────────────────────────────

class SimulationCreate(BaseModel):
    project_id: str
    name: str = Field(..., min_length=1, max_length=255)
    intervention_type: str = "habitat_restoration"
    zone_ids: Optional[List[str]] = None
    restoration_area_ha: Optional[float] = None
    parameters: Optional[Dict[str, Any]] = None


class SimulationResponse(BaseModel):
    id: str
    project_id: str
    name: str
    intervention_type: str
    zone_ids: Optional[List[str]] = None
    restoration_area_ha: Optional[float] = None

    # Results
    baseline_connectivity: Optional[float] = None
    simulated_connectivity: Optional[float] = None
    improvement: Optional[float] = None
    percentage_change: Optional[float] = None
    result: Optional[Dict[str, Any]] = None

    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ScenarioComparison(BaseModel):
    """Comparison of multiple simulation scenarios."""
    project_id: str
    baseline_connectivity: float
    scenarios: List[SimulationResponse]


# ──────────────────────────── GeoJSON ────────────────────────────

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any] = {}


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature] = []


# ──────────────────────────── Dashboard ────────────────────────────

class DashboardStats(BaseModel):
    """Dashboard summary statistics."""
    project_name: str
    region_name: Optional[str] = None
    species_name: Optional[str] = None
    habitat_score: Optional[float] = None
    connectivity_score: Optional[float] = None
    total_habitat_patches: int = 0
    total_corridors: int = 0
    total_priority_zones: int = 0
    critical_zones: int = 0
    total_observations: int = 0
    evidence_quality: Optional[str] = None
