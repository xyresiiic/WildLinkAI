"""
WildLink AI — Simulation API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Simulation, Project, JobStatus
from app.schemas import SimulationCreate, SimulationResponse, ScenarioComparison
from app.utils import success_response
from app.services.simulation_service import run_simulation

router = APIRouter(prefix="/simulations", tags=["Simulations"])


@router.post("", response_model=None, status_code=202)
@router.post("/run", response_model=None, status_code=202)
async def create_simulation(
    data: SimulationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create and run a What-If simulation scenario."""
    # Verify project
    result = await db.execute(select(Project).where(Project.id == data.project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sim = Simulation(
        project_id=data.project_id,
        name=data.name,
        intervention_type=data.intervention_type,
        zone_ids=data.zone_ids,
        restoration_area_ha=data.restoration_area_ha,
        parameters=data.parameters,
        status=JobStatus.QUEUED,
    )
    db.add(sim)
    await db.commit()
    await db.refresh(sim)

    # Queue background simulation
    background_tasks.add_task(
        run_simulation,
        str(sim.id),
        str(data.project_id),
    )

    return success_response(
        data=SimulationResponse.model_validate(sim).model_dump(mode="json"),
        message="Simulation queued"
    )


@router.get("/{simulation_id}", response_model=None)
async def get_simulation(simulation_id: str, db: AsyncSession = Depends(get_db)):
    """Get a simulation result."""
    result = await db.execute(select(Simulation).where(Simulation.id == simulation_id))
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return success_response(data=SimulationResponse.model_validate(sim).model_dump(mode="json"))


@router.get("/project/{project_id}", response_model=None)
async def get_project_simulations(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get all simulations for a project (scenario comparison)."""
    result = await db.execute(
        select(Simulation)
        .where(Simulation.project_id == project_id)
        .order_by(Simulation.created_at)
    )
    simulations = result.scalars().all()

    # Calculate baseline from first completed sim or from project data
    baseline = 0.0
    for sim in simulations:
        if sim.baseline_connectivity is not None:
            baseline = sim.baseline_connectivity
            break

    scenarios = [SimulationResponse.model_validate(s).model_dump(mode="json") for s in simulations]

    return success_response(data={
        "project_id": project_id,
        "baseline_connectivity": baseline,
        "scenarios": scenarios,
        "count": len(scenarios)
    })
