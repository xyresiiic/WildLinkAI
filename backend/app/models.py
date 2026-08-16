"""
WildLink AI — SQLAlchemy Models

All database models for the WildLink platform.
Uses String(36) for UUID primary keys and foreign keys for cross-DB compatibility.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, Text, DateTime,
    ForeignKey, Boolean, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# ──────────────────────────── Enums ────────────────────────────

class ProjectStatus(str, enum.Enum):
    CREATED = "created"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceQuality(str, enum.Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


# ──────────────────────────── User ────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


# ──────────────────────────── Species ────────────────────────────

class Species(Base):
    __tablename__ = "species"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    common_name = Column(String(255), nullable=False)
    scientific_name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    habitat_preferences = Column(JSON, nullable=True)
    conservation_status = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)

    # Relationships
    observations = relationship("Observation", back_populates="species", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="species")


# ──────────────────────────── Project ────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    region_geometry = Column(JSON, nullable=True)
    region_name = Column(String(255), nullable=True)
    species_id = Column(String(36), ForeignKey("species.id"), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(ProjectStatus), default=ProjectStatus.CREATED, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    owner = relationship("User", back_populates="projects")
    species = relationship("Species", back_populates="projects")
    habitat_zones = relationship("HabitatZone", back_populates="project", cascade="all, delete-orphan")
    corridors = relationship("Corridor", back_populates="project", cascade="all, delete-orphan")
    priority_zones = relationship("PriorityZone", back_populates="project", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="project", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="project", cascade="all, delete-orphan")


# ──────────────────────────── Observation ────────────────────────────

class Observation(Base):
    __tablename__ = "observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    species_id = Column(String(36), ForeignKey("species.id"), nullable=False)
    location = Column(JSON, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)

    # Relationships
    species = relationship("Species", back_populates="observations")


# ──────────────────────────── Dataset ────────────────────────────

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    source = Column(String(255), nullable=True)
    type = Column(String(50), nullable=False)
    version = Column(String(50), nullable=True)
    crs = Column(String(50), default="EPSG:4326")
    quality = Column(SAEnum(EvidenceQuality), default=EvidenceQuality.MODERATE)
    file_path = Column(String(500), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ──────────────────────────── Habitat Zone ────────────────────────────

class HabitatZone(Base):
    __tablename__ = "habitat_zones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    geometry = Column(JSON, nullable=False)
    suitability_score = Column(Float, nullable=False)
    area_hectares = Column(Float, nullable=True)
    patch_id = Column(Integer, nullable=True)
    perimeter_km = Column(Float, nullable=True)
    compactness = Column(Float, nullable=True)
    nearest_patch_distance_km = Column(Float, nullable=True)
    fragmentation_level = Column(String(20), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="habitat_zones")


# ──────────────────────────── Corridor ────────────────────────────

class Corridor(Base):
    __tablename__ = "corridors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    geometry = Column(JSON, nullable=False)
    source_patch_id = Column(Integer, nullable=True)
    target_patch_id = Column(Integer, nullable=True)
    connectivity_score = Column(Float, nullable=True)
    resistance_score = Column(Float, nullable=True)
    length_km = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="corridors")


# ──────────────────────────── Priority Zone ────────────────────────────

class PriorityZone(Base):
    __tablename__ = "priority_zones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    geometry = Column(JSON, nullable=False)
    rank = Column(Integer, nullable=True)
    priority_score = Column(Float, nullable=False)
    priority_level = Column(String(20), nullable=True)

    # Factor scores
    habitat_score = Column(Float, nullable=True)
    connectivity_score = Column(Float, nullable=True)
    species_score = Column(Float, nullable=True)
    restoration_score = Column(Float, nullable=True)
    constraint_score = Column(Float, nullable=True)

    # Explainability
    dominant_factor = Column(String(50), nullable=True)
    explanation = Column(Text, nullable=True)
    evidence_quality = Column(SAEnum(EvidenceQuality), default=EvidenceQuality.MODERATE)
    factors_json = Column(JSON, nullable=True)

    # Area
    area_hectares = Column(Float, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="priority_zones")


# ──────────────────────────── Simulation ────────────────────────────

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    intervention_type = Column(String(50), default="habitat_restoration")
    zone_ids = Column(JSON, nullable=True)
    parameters = Column(JSON, nullable=True)
    restoration_area_ha = Column(Float, nullable=True)

    # Results
    baseline_connectivity = Column(Float, nullable=True)
    simulated_connectivity = Column(Float, nullable=True)
    improvement = Column(Float, nullable=True)
    percentage_change = Column(Float, nullable=True)
    result = Column(JSON, nullable=True)

    status = Column(SAEnum(JobStatus), default=JobStatus.QUEUED)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="simulations")


# ──────────────────────────── Analysis Job ────────────────────────────

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(SAEnum(JobStatus), default=JobStatus.QUEUED, nullable=False)
    progress = Column(Integer, default=0)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="analysis_jobs")
