"""
WildLink AI — Projects API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from app.database.connection import get_db
from app.models.models import Project, Species, HabitatZone, Corridor, PriorityZone, Simulation, Observation
from app.schemas.schemas import (
    ProjectCreate, ProjectResponse, ProjectDetail, DashboardStats,
    SpeciesResponse
)
from app.utils.helpers import success_response
import uuid

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=None)
async def list_projects(db: AsyncSession = Depends(get_db)):
    """Get all projects."""
    result = await db.execute(
        select(Project).options(selectinload(Project.species)).order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()
    return success_response(
        data=[ProjectResponse.model_validate(p).model_dump() for p in projects],
        message=f"Found {len(projects)} projects"
    )


@router.get("/{project_id}", response_model=None)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get project details with analysis summaries."""
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.species))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Count related entities
    habitat_count = (await db.execute(
        select(func.count()).where(HabitatZone.project_id == project_id)
    )).scalar() or 0

    corridor_count = (await db.execute(
        select(func.count()).where(Corridor.project_id == project_id)
    )).scalar() or 0

    priority_count = (await db.execute(
        select(func.count()).where(PriorityZone.project_id == project_id)
    )).scalar() or 0

    simulation_count = (await db.execute(
        select(func.count()).where(Simulation.project_id == project_id)
    )).scalar() or 0

    # Average scores
    avg_habitat = (await db.execute(
        select(func.avg(HabitatZone.suitability_score)).where(HabitatZone.project_id == project_id)
    )).scalar()

    avg_connectivity = (await db.execute(
        select(func.avg(Corridor.connectivity_score)).where(Corridor.project_id == project_id)
    )).scalar()

    detail = ProjectDetail(
        id=project.id,
        name=project.name,
        description=project.description,
        region_name=project.region_name,
        species_id=project.species_id,
        status=project.status.value if project.status else "created",
        created_at=project.created_at,
        species=SpeciesResponse.model_validate(project.species) if project.species else None,
        habitat_zones_count=habitat_count,
        corridors_count=corridor_count,
        priority_zones_count=priority_count,
        simulations_count=simulation_count,
        avg_habitat_score=round(avg_habitat * 100, 1) if avg_habitat else None,
        avg_connectivity_score=round(avg_connectivity, 1) if avg_connectivity else None,
    )

    return success_response(data=detail.model_dump())


@router.post("", response_model=None, status_code=201)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new conservation project."""
    # Use a default user ID for MVP (no auth yet)
    default_user_id = "00000000-0000-0000-0000-000000000001"

    project = Project(
        name=data.name,
        description=data.description,
        region_name=data.region_name,
        species_id=str(data.species_id) if data.species_id else None,
        created_by=default_user_id,
    )

    # Handle region GeoJSON if provided
    if data.region_geojson:
        project.region_geometry = data.region_geojson

    db.add(project)
    await db.commit()

    # Eagerly load relationship for Pydantic validation
    res = await db.execute(
        select(Project).options(selectinload(Project.species)).where(Project.id == project.id)
    )
    full_project = res.scalar_one()

    return success_response(
        data=ProjectResponse.model_validate(full_project).model_dump(mode="json"),
        message="Project created"
    )


@router.delete("/{project_id}", response_model=None)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a project and all its analysis data."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()
    return success_response(message="Project deleted")


@router.get("/{project_id}/dashboard", response_model=None)
async def get_dashboard(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics for a project."""
    result = await db.execute(
        select(Project).options(selectinload(Project.species)).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Counts
    habitat_count = (await db.execute(
        select(func.count()).where(HabitatZone.project_id == project_id)
    )).scalar() or 0

    corridor_count = (await db.execute(
        select(func.count()).where(Corridor.project_id == project_id)
    )).scalar() or 0

    priority_count = (await db.execute(
        select(func.count()).where(PriorityZone.project_id == project_id)
    )).scalar() or 0

    critical_count = (await db.execute(
        select(func.count()).where(
            PriorityZone.project_id == project_id,
            PriorityZone.priority_level.in_(["critical", "high"])
        )
    )).scalar() or 0

    # Observation count for species
    obs_count = 0
    if project.species_id:
        obs_count = (await db.execute(
            select(func.count()).where(Observation.species_id == project.species_id)
        )).scalar() or 0

    # Average scores
    avg_habitat = (await db.execute(
        select(func.avg(HabitatZone.suitability_score)).where(HabitatZone.project_id == project_id)
    )).scalar()

    avg_connectivity = (await db.execute(
        select(func.avg(Corridor.connectivity_score)).where(Corridor.project_id == project_id)
    )).scalar()

    stats = DashboardStats(
        project_name=project.name,
        region_name=project.region_name,
        species_name=project.species.common_name if project.species else None,
        habitat_score=round(avg_habitat * 100, 1) if avg_habitat else None,
        connectivity_score=round(avg_connectivity, 1) if avg_connectivity else None,
        total_habitat_patches=habitat_count,
        total_corridors=corridor_count,
        total_priority_zones=priority_count,
        critical_zones=critical_count,
        total_observations=obs_count,
    )

    return success_response(data=stats.model_dump(mode="json"))


@router.get("/{project_id}/export", response_model=None)
async def export_project_data(project_id: str, db: AsyncSession = Depends(get_db)):
    """Export complete project GIS data layers and executive conservation summary as JSON."""
    result = await db.execute(
        select(Project).options(selectinload(Project.species)).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Load all layers
    hz_res = await db.execute(select(HabitatZone).where(HabitatZone.project_id == project_id))
    cor_res = await db.execute(select(Corridor).where(Corridor.project_id == project_id))
    pz_res = await db.execute(select(PriorityZone).where(PriorityZone.project_id == project_id).order_by(PriorityZone.rank))
    sim_res = await db.execute(select(Simulation).where(Simulation.project_id == project_id))

    zones = hz_res.scalars().all()
    corridors = cor_res.scalars().all()
    priority_zones = pz_res.scalars().all()
    simulations = sim_res.scalars().all()

    export_bundle = {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "region_name": project.region_name,
            "species": project.species.common_name if project.species else None,
            "conservation_status": project.species.conservation_status if project.species else None,
            "created_at": project.created_at.isoformat() if project.created_at else None,
        },
        "summary": {
            "habitat_zones_count": len(zones),
            "corridors_count": len(corridors),
            "priority_zones_count": len(priority_zones),
            "simulations_count": len(simulations),
        },
        "habitat_zones": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": z.geometry,
                "properties": {
                    "suitability_score": z.suitability_score,
                    "area_hectares": z.area_hectares,
                    "fragmentation_level": z.fragmentation_level,
                }
            } for z in zones]
        },
        "corridors": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": c.geometry,
                "properties": {
                    "connectivity_score": c.connectivity_score,
                    "resistance_score": c.resistance_score,
                    "length_km": c.length_km,
                }
            } for c in corridors]
        },
        "priority_zones": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": pz.geometry,
                "properties": {
                    "rank": pz.rank,
                    "priority_score": pz.priority_score,
                    "priority_level": pz.priority_level,
                    "dominant_factor": pz.dominant_factor,
                    "explanation": pz.explanation,
                    "recommended_action": pz.factors_json.get("recommended_action") if pz.factors_json else None,
                }
            } for pz in priority_zones]
        },
        "simulations": [
            {
                "name": s.name,
                "intervention_type": s.intervention_type,
                "baseline_connectivity": s.baseline_connectivity,
                "simulated_connectivity": s.simulated_connectivity,
                "improvement": s.improvement,
                "percentage_change": s.percentage_change,
            } for s in simulations if s.status == "completed"
        ]
    }

    return success_response(data=export_bundle, message="Project data bundle exported successfully")
