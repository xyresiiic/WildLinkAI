"""
===============================================================================
WildLink AI — Data Models Package (SQLAlchemy ORM Entities)
===============================================================================
Defines the relational database schema, tables, and enumerations for:
- Core entities: User, Species, Project, Observation, Dataset
- GIS output entities: HabitatZone, Corridor, PriorityZone
- Scenario entities: Simulation, AnalysisJob
- System enumerations: UserRole, ProjectStatus, JobStatus, EvidenceQuality
"""

__title__ = "WildLink Data Models Package"
__description__ = "SQLAlchemy 2.0 ORM data layer and database entities"

from app.models.conservation_models import (
    Base,
    User,
    Species,
    Project,
    Observation,
    Dataset,
    HabitatZone,
    Corridor,
    PriorityZone,
    Simulation,
    AnalysisJob,
    ProjectStatus,
    JobStatus,
    EvidenceQuality,
    UserRole,
)

__all__ = [
    "Base",
    "User",
    "Species",
    "Project",
    "Observation",
    "Dataset",
    "HabitatZone",
    "Corridor",
    "PriorityZone",
    "Simulation",
    "AnalysisJob",
    "ProjectStatus",
    "JobStatus",
    "EvidenceQuality",
    "UserRole",
]
