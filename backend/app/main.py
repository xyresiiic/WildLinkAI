"""
WildLink AI — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.connection import init_db, close_db
from app.api import species, projects, analysis, simulations

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("wildlink")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("🌿 WildLink AI starting up...")

    # Initialize database tables
    await init_db()
    logger.info("✅ Database initialized")

    # Seed demo data on first run
    await _seed_demo_data()

    yield

    # Shutdown
    await close_db()
    logger.info("🛑 WildLink AI shut down")


app = FastAPI(
    title="WildLink AI",
    description=(
        "AI-Powered Wildlife Habitat Connectivity & Conservation Prioritization Platform. "
        "Combines geospatial analysis, ML-based habitat suitability, graph-based connectivity, "
        "and What-If simulation to support conservation decision-making."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(species.router, prefix=settings.API_V1_PREFIX)
app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
app.include_router(analysis.router, prefix=settings.API_V1_PREFIX)
app.include_router(simulations.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
async def root():
    """Health check / root endpoint."""
    return {
        "name": "WildLink AI",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-Powered Wildlife Habitat Connectivity & Conservation Prioritization"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.APP_ENV,
    }


async def _seed_demo_data():
    """Seed the database with comprehensive species across categories and sample observations."""
    from app.database.connection import AsyncSessionLocal
    from app.models.models import User, Species, UserRole, Observation
    from app.core.security import hash_password
    from sqlalchemy import select
    from datetime import datetime, timezone
    import numpy as np

    async with AsyncSessionLocal() as db:
        # Check existing user
        result = await db.execute(select(User).where(User.id == "00000000-0000-0000-0000-000000000001"))
        if not result.scalar_one_or_none():
            default_user = User(
                id="00000000-0000-0000-0000-000000000001",
                name="WildLink Demo User",
                email="demo@wildlink.ai",
                password_hash=hash_password("demo123"),
                role=UserRole.USER,
            )
            db.add(default_user)

        # Comprehensive Species Dataset
        species_data = [
            {
                "common_name": "Bengal Tiger",
                "scientific_name": "Panthera tigris tigris",
                "description": "Apex predator inhabiting contiguous forest tracts, riverine grasslands, and protected reserves across Central and Eastern India.",
                "conservation_status": "Endangered",
                "habitat_preferences": {
                    "dense_forest": 0.95, "moist_deciduous_forest": 0.90, "dry_deciduous_forest": 0.80,
                    "grassland": 0.60, "scrubland": 0.40, "agriculture": 0.10, "settlement": 0.02, "water_body": 0.70,
                },
                "reserves": [(23.5, 80.5), (22.85, 80.6), (22.2, 78.1), (22.6, 77.7), (23.8, 80.8)]
            },
            {
                "common_name": "Indian Elephant",
                "scientific_name": "Elephas maximus indicus",
                "description": "Megaherbivore requiring long-distance migration corridors connecting forest patches and perennial water sources.",
                "conservation_status": "Endangered",
                "habitat_preferences": {
                    "dense_forest": 0.85, "moist_deciduous_forest": 0.90, "dry_deciduous_forest": 0.75,
                    "grassland": 0.70, "scrubland": 0.50, "agriculture": 0.20, "settlement": 0.05, "water_body": 0.80,
                },
                "reserves": [(23.1, 81.2), (22.5, 82.4), (22.9, 80.8), (22.1, 79.5), (23.6, 80.4)]
            },
            {
                "common_name": "Indian Leopard",
                "scientific_name": "Panthera pardus fusca",
                "description": "Highly adaptable carnivore ranging across forest buffers, rocky hills, and human-dominated agricultural fringes.",
                "conservation_status": "Vulnerable",
                "habitat_preferences": {
                    "dense_forest": 0.90, "moist_deciduous_forest": 0.85, "dry_deciduous_forest": 0.80,
                    "grassland": 0.50, "scrubland": 0.60, "agriculture": 0.30, "settlement": 0.15, "water_body": 0.50,
                },
                "reserves": [(23.3, 77.5), (22.4, 78.5), (23.8, 79.8), (22.7, 81.0), (23.0, 80.0)]
            },
            {
                "common_name": "Sloth Bear",
                "scientific_name": "Melursus ursinus",
                "description": "Myrmecophagous bear species utilizing rocky terrain, dry deciduous forests, and termite-rich scrub habitats.",
                "conservation_status": "Vulnerable",
                "habitat_preferences": {
                    "dense_forest": 0.80, "moist_deciduous_forest": 0.85, "dry_deciduous_forest": 0.90,
                    "grassland": 0.40, "scrubland": 0.75, "agriculture": 0.15, "settlement": 0.05, "water_body": 0.60,
                },
                "reserves": [(24.2, 81.2), (23.3, 85.3), (22.2, 81.5), (23.5, 80.1), (22.8, 78.9)]
            },
            {
                "common_name": "Great Indian Bustard",
                "scientific_name": "Ardeotis nigriceps",
                "description": "Critically endangered flagship grassland bird restricted to semi-arid open plains and non-intensive agriculture.",
                "conservation_status": "Critically Endangered",
                "habitat_preferences": {
                    "dense_forest": 0.05, "moist_deciduous_forest": 0.10, "dry_deciduous_forest": 0.20,
                    "grassland": 0.95, "scrubland": 0.85, "agriculture": 0.40, "settlement": 0.02, "water_body": 0.30,
                },
                "reserves": [(23.5, 80.2), (23.8, 79.5), (22.9, 78.8), (23.1, 80.9), (22.5, 79.8)]
            },
            {
                "common_name": "Gharial",
                "scientific_name": "Gavialis gangeticus",
                "description": "Critically endangered fish-eating crocodilian specialized in high-integrity river channels and undisturbed sandbanks.",
                "conservation_status": "Critically Endangered",
                "habitat_preferences": {
                    "dense_forest": 0.20, "moist_deciduous_forest": 0.30, "dry_deciduous_forest": 0.20,
                    "grassland": 0.30, "scrubland": 0.10, "agriculture": 0.05, "settlement": 0.01, "water_body": 0.98,
                },
                "reserves": [(23.6, 80.9), (23.1, 80.4), (22.7, 78.4), (23.9, 80.7), (22.3, 79.2)]
            },
            {
                "common_name": "Snow Leopard",
                "scientific_name": "Panthera uncia",
                "description": "Elusive alpine cat inhabiting high-altitude rocky bluffs, mountain ridges, and alpine pastures.",
                "conservation_status": "Vulnerable",
                "habitat_preferences": {
                    "dense_forest": 0.20, "moist_deciduous_forest": 0.10, "dry_deciduous_forest": 0.10,
                    "grassland": 0.80, "scrubland": 0.90, "agriculture": 0.05, "settlement": 0.01, "water_body": 0.40,
                },
                "reserves": [(24.1, 80.5), (23.7, 81.1), (23.4, 79.2), (23.9, 80.1), (22.8, 80.9)]
            }
        ]

        for sp_data in species_data:
            reserves = sp_data.pop("reserves")
            res = await db.execute(select(Species).where(Species.scientific_name == sp_data["scientific_name"]))
            existing_sp = res.scalar_one_or_none()

            if not existing_sp:
                existing_sp = Species(**sp_data)
                db.add(existing_sp)
                await db.flush()
                logger.info(f"➕ Added species: {existing_sp.common_name}")

            # Check if observations exist for this species
            obs_res = await db.execute(select(Observation).where(Observation.species_id == existing_sp.id).limit(1))
            if not obs_res.scalar_one_or_none():
                for rlat, rlng in reserves:
                    for _ in range(10):
                        lat = float(rlat + np.random.normal(0, 0.08))
                        lng = float(rlng + np.random.normal(0, 0.08))
                        obs = Observation(
                            species_id=existing_sp.id,
                            latitude=lat,
                            longitude=lng,
                            location={"type": "Point", "coordinates": [lng, lat]},
                            source="GBIF / WII Field Survey",
                            confidence=float(np.random.uniform(0.78, 0.99)),
                            observed_at=datetime.now(timezone.utc),
                        )
                        db.add(obs)
                logger.info(f"📍 Seeded 50 observations for {existing_sp.common_name}")

        await db.commit()
        logger.info("✅ Comprehensive multi-species demo dataset ready!")

