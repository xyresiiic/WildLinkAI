"""
WildLink AI — Simulation Service

Runs What-If conservation simulations as background tasks.
"""
import logging
from datetime import datetime, timezone
from sqlalchemy import select, update
from app.database.connection import AsyncSessionLocal
from app.models.models import Simulation, JobStatus

logger = logging.getLogger("wildlink.simulation")


async def run_simulation(simulation_id: str, project_id: str):
    """
    Run a What-If simulation as a background task.

    Process:
    1. Load baseline landscape model
    2. Apply intervention (reduce resistance in target zones)
    3. Recalculate connectivity
    4. Compare with baseline
    5. Store results
    """
    async with AsyncSessionLocal() as db:
        try:
            # Mark as running
            await db.execute(
                update(Simulation)
                .where(Simulation.id == simulation_id)
                .values(status=JobStatus.RUNNING)
            )
            await db.commit()

            logger.info(f"Starting simulation {simulation_id} for project {project_id}")

            # Run simulation engine
            from app.engines.simulation_engine import SimulationEngine
            engine = SimulationEngine(project_id, simulation_id, db)
            result = await engine.run()

            # Update with results
            await db.execute(
                update(Simulation)
                .where(Simulation.id == simulation_id)
                .values(
                    status=JobStatus.COMPLETED,
                    baseline_connectivity=result.get("baseline_connectivity"),
                    simulated_connectivity=result.get("simulated_connectivity"),
                    improvement=result.get("improvement"),
                    percentage_change=result.get("percentage_change"),
                    result=result,
                )
            )
            await db.commit()

            logger.info(f"Simulation {simulation_id} completed")

        except Exception as e:
            logger.error(f"Simulation failed: {e}", exc_info=True)
            await db.execute(
                update(Simulation)
                .where(Simulation.id == simulation_id)
                .values(
                    status=JobStatus.FAILED,
                    result={"error": str(e)}
                )
            )
            await db.commit()
