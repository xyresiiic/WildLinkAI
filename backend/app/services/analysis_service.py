"""
WildLink AI — Analysis Service

Orchestrates the full analysis pipeline:
  Data → Habitat Suitability → Fragmentation → Resistance → Connectivity → Priority
"""
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, update
from app.database import AsyncSessionLocal
from app.models import AnalysisJob, Project, JobStatus

logger = logging.getLogger("wildlink.analysis")


async def run_full_analysis(
    job_id: str,
    project_id: str,
    analysis_type: str,
    parameters: dict
):
    """
    Run the full analysis pipeline as a background task.

    Pipeline order:
    1. Habitat Suitability
    2. Fragmentation
    3. Resistance Surface
    4. Connectivity
    5. Priority Scoring
    """
    async with AsyncSessionLocal() as db:
        try:
            # Mark job as running
            await db.execute(
                update(AnalysisJob)
                .where(AnalysisJob.id == job_id)
                .values(
                    status=JobStatus.RUNNING,
                    started_at=datetime.now(timezone.utc),
                    progress=0
                )
            )
            await db.commit()

            logger.info(f"Starting {analysis_type} analysis for project {project_id}")

            if analysis_type in ("habitat", "full"):
                await _update_progress(db, job_id, 10, "Running habitat suitability...")
                from app.engines.habitat_engine import HabitatEngine
                engine = HabitatEngine(project_id, db)
                await engine.run()
                await db.commit()

            if analysis_type in ("fragmentation", "full"):
                await _update_progress(db, job_id, 30, "Running fragmentation analysis...")
                from app.engines.fragmentation_engine import FragmentationEngine
                engine = FragmentationEngine(project_id, db)
                await engine.run()
                await db.commit()

            if analysis_type in ("connectivity", "full"):
                await _update_progress(db, job_id, 50, "Building resistance surface...")
                from app.engines.resistance_engine import ResistanceEngine
                r_engine = ResistanceEngine(project_id, db)
                await r_engine.run()
                await db.commit()

                await _update_progress(db, job_id, 65, "Running connectivity analysis...")
                from app.engines.connectivity_engine import ConnectivityEngine
                c_engine = ConnectivityEngine(project_id, db)
                await c_engine.run()
                await db.commit()

            if analysis_type in ("priority", "full"):
                await _update_progress(db, job_id, 80, "Calculating priorities...")
                from app.engines.priority_engine import PriorityEngine
                engine = PriorityEngine(project_id, db)
                await engine.run()
                await db.commit()

            # Mark completed
            await db.execute(
                update(AnalysisJob)
                .where(AnalysisJob.id == job_id)
                .values(
                    status=JobStatus.COMPLETED,
                    progress=100,
                    completed_at=datetime.now(timezone.utc)
                )
            )

            # Update project status
            await db.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(status="completed")
            )
            await db.commit()

            logger.info(f"Analysis completed for project {project_id}")

        except Exception as e:
            logger.error(f"Analysis failed for project {project_id}: {e}", exc_info=True)
            await db.execute(
                update(AnalysisJob)
                .where(AnalysisJob.id == job_id)
                .values(
                    status=JobStatus.FAILED,
                    error=str(e),
                    completed_at=datetime.now(timezone.utc)
                )
            )
            await db.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(status="failed")
            )
            await db.commit()


async def _update_progress(db, job_id: str, progress: int, message: str = ""):
    """Update job progress."""
    logger.info(f"Job {job_id}: {progress}% — {message}")
    await db.execute(
        update(AnalysisJob)
        .where(AnalysisJob.id == job_id)
        .values(progress=progress)
    )
    await db.commit()
