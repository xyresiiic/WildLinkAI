"""
WildLink AI — Analysis API Routes

Triggers habitat, fragmentation, connectivity, and priority analyses.
Long-running analyses use background jobs.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import (
    Project, AnalysisJob, JobStatus, HabitatZone, Corridor, PriorityZone, Observation
)
from app.schemas import (
    AnalysisRequest, AnalysisJobResponse,
    HabitatZoneResponse, CorridorResponse, PriorityZoneResponse,
    ObservationResponse, GeoJSONFeatureCollection
)
from app.utils import success_response
from app.services.analysis_service import run_full_analysis
from datetime import datetime, timezone

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/run", response_model=None, status_code=202)
async def trigger_analysis(
    data: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger an analysis pipeline for a project."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == data.project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create analysis job
    job = AnalysisJob(
        project_id=data.project_id,
        type=data.type,
        status=JobStatus.QUEUED,
        progress=0,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # On serverless (Vercel/Lambda), execute directly to avoid container freeze
    import os
    is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
    if is_serverless:
        await run_full_analysis(
            str(job.id),
            str(data.project_id),
            data.type,
            data.parameters or {}
        )
        res = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job.id))
        job = res.scalar_one_or_none() or job
    else:
        background_tasks.add_task(
            run_full_analysis,
            str(job.id),
            str(data.project_id),
            data.type,
            data.parameters or {}
        )

    return success_response(
        data=AnalysisJobResponse.model_validate(job).model_dump(mode="json"),
        message=f"Analysis '{data.type}' {'completed' if is_serverless else 'queued'} for project"
    )


@router.get("/jobs/{job_id}", response_model=None)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """Check the status of an analysis job."""
    result = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return success_response(data=AnalysisJobResponse.model_validate(job).model_dump(mode="json"))


@router.get("/habitat/{project_id}", response_model=None)
async def get_habitat_zones(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get habitat zones for a project as GeoJSON."""
    result = await db.execute(
        select(HabitatZone).where(HabitatZone.project_id == project_id)
        .order_by(HabitatZone.suitability_score.desc())
    )
    zones = result.scalars().all()

    features = []
    for zone in zones:
        features.append({
            "type": "Feature",
            "geometry": _geometry_to_geojson(zone.geometry) if zone.geometry else None,
            "properties": {
                "id": str(zone.id),
                "suitability_score": zone.suitability_score,
                "area_hectares": zone.area_hectares,
                "patch_id": zone.patch_id,
                "fragmentation_level": zone.fragmentation_level,
            }
        })

    return success_response(data={
        "type": "FeatureCollection",
        "features": features,
        "count": len(features)
    })


@router.get("/corridors/{project_id}", response_model=None)
async def get_corridors(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get corridors for a project as GeoJSON."""
    result = await db.execute(
        select(Corridor).where(Corridor.project_id == project_id)
        .order_by(Corridor.connectivity_score.desc())
    )
    corridors = result.scalars().all()

    features = []
    for corridor in corridors:
        features.append({
            "type": "Feature",
            "geometry": _geometry_to_geojson(corridor.geometry) if corridor.geometry else None,
            "properties": {
                "id": str(corridor.id),
                "connectivity_score": corridor.connectivity_score,
                "resistance_score": corridor.resistance_score,
                "length_km": corridor.length_km,
                "source_patch_id": corridor.source_patch_id,
                "target_patch_id": corridor.target_patch_id,
            }
        })

    return success_response(data={
        "type": "FeatureCollection",
        "features": features,
        "count": len(features)
    })


@router.get("/priority/{project_id}", response_model=None)
async def get_priority_zones(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get priority zones for a project as GeoJSON."""
    result = await db.execute(
        select(PriorityZone).where(PriorityZone.project_id == project_id)
        .order_by(PriorityZone.rank)
    )
    zones = result.scalars().all()

    features = []
    for zone in zones:
        features.append({
            "type": "Feature",
            "geometry": _geometry_to_geojson(zone.geometry) if zone.geometry else None,
            "properties": {
                "id": str(zone.id),
                "rank": zone.rank,
                "priority_score": zone.priority_score,
                "priority_level": zone.priority_level,
                "habitat_score": zone.habitat_score,
                "connectivity_score": zone.connectivity_score,
                "species_score": zone.species_score,
                "restoration_score": zone.restoration_score,
                "dominant_factor": zone.dominant_factor,
                "explanation": zone.explanation,
                "evidence_quality": zone.evidence_quality.value if zone.evidence_quality else None,
                "area_hectares": zone.area_hectares,
                "recommended_action": (zone.factors_json.get("recommended_action") if zone.factors_json and isinstance(zone.factors_json, dict) else "Conservation Buffer"),
                "factors_json": zone.factors_json,
            }
        })

    return success_response(data={
        "type": "FeatureCollection",
        "features": features,
        "count": len(features)
    })


@router.get("/observations/{project_id}", response_model=None)
async def get_observations(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get species observations for a project as GeoJSON."""
    # Get species_id from project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or not project.species_id:
        raise HTTPException(status_code=404, detail="Project or species not found")

    obs_result = await db.execute(
        select(Observation).where(Observation.species_id == project.species_id)
    )
    observations = obs_result.scalars().all()

    features = []
    for obs in observations:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [obs.longitude, obs.latitude]
            },
            "properties": {
                "id": str(obs.id),
                "observed_at": obs.observed_at.isoformat() if obs.observed_at else None,
                "source": obs.source,
                "confidence": obs.confidence,
            }
        })

    return success_response(data={
        "type": "FeatureCollection",
        "features": features,
        "count": len(features)
    })


def _geometry_to_geojson(geom):
    """Convert geometry to GeoJSON dict."""
    if isinstance(geom, dict):
        return geom
    return None
