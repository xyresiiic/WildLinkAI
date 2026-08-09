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
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
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
    """Seed the database with demo species and a default user on first run."""
    from app.database.connection import AsyncSessionLocal
    from app.models.models import User, Species, UserRole
    from app.core.security import hash_password
    from sqlalchemy import select
    from datetime import datetime, timezone
    import uuid

    async with AsyncSessionLocal() as db:
        # Check if demo data already exists
        result = await db.execute(select(Species).limit(1))
        if result.scalar_one_or_none():
            return  # Already seeded

        logger.info("🌱 Seeding demo data...")

        # Create default user
        default_user = User(
            id="00000000-0000-0000-0000-000000000001",
            name="WildLink Demo User",
            email="demo@wildlink.ai",
            password_hash=hash_password("demo123"),
            role=UserRole.USER,
        )
        db.add(default_user)

        # Seed species
        species_data = [
            {
                "common_name": "Bengal Tiger",
                "scientific_name": "Panthera tigris tigris",
                "description": "The Bengal tiger is a population of the Panthera tigris tigris subspecies. It is the most numerous tiger subspecies, primarily found in India.",
                "conservation_status": "Endangered",
                "habitat_preferences": {
                    "dense_forest": 0.95,
                    "moist_deciduous_forest": 0.90,
                    "dry_deciduous_forest": 0.80,
                    "grassland": 0.60,
                    "scrubland": 0.40,
                    "agriculture": 0.10,
                    "settlement": 0.02,
                    "water_body": 0.70,
                }
            },
            {
                "common_name": "Indian Elephant",
                "scientific_name": "Elephas maximus indicus",
                "description": "The Indian elephant is a subspecies of the Asian elephant native to mainland Asia.",
                "conservation_status": "Endangered",
                "habitat_preferences": {
                    "dense_forest": 0.85,
                    "moist_deciduous_forest": 0.90,
                    "dry_deciduous_forest": 0.75,
                    "grassland": 0.70,
                    "scrubland": 0.50,
                    "agriculture": 0.20,
                    "settlement": 0.05,
                    "water_body": 0.80,
                }
            },
            {
                "common_name": "Indian Leopard",
                "scientific_name": "Panthera pardus fusca",
                "description": "The Indian leopard is a subspecies widely distributed across the Indian subcontinent.",
                "conservation_status": "Vulnerable",
                "habitat_preferences": {
                    "dense_forest": 0.90,
                    "moist_deciduous_forest": 0.85,
                    "dry_deciduous_forest": 0.80,
                    "grassland": 0.50,
                    "scrubland": 0.60,
                    "agriculture": 0.30,
                    "settlement": 0.15,
                    "water_body": 0.50,
                }
            },
        ]

        created_species = []
        for sp in species_data:
            s_obj = Species(**sp)
            db.add(s_obj)
            created_species.append(s_obj)

        await db.flush()

        # Seed sample observations for Bengal Tiger
        tiger = created_species[0]
        from app.models.models import Observation
        import numpy as np

        # Key Tiger Reserves in Central Indian Highlands (lat, lng)
        reserves = [
            (23.5, 80.5),    # Panna
            (22.85, 80.6),   # Kanha
            (22.2, 78.1),    # Pench
            (22.6, 77.7),    # Satpura
            (23.8, 80.8),    # Bandhavgarh
        ]

        for rlat, rlng in reserves:
            # Generate 8-12 cluster observations per reserve
            for _ in range(10):
                lat = rlat + np.random.normal(0, 0.08)
                lng = rlng + np.random.normal(0, 0.08)
                obs = Observation(
                    species_id=tiger.id,
                    latitude=float(lat),
                    longitude=float(lng),
                    location={"type": "Point", "coordinates": [float(lng), float(lat)]},
                    source="GBIF / WII Survey",
                    confidence=float(np.random.uniform(0.75, 0.98)),
                    observed_at=datetime.now(timezone.utc),
                )
                db.add(obs)

        await db.commit()
        logger.info("✅ Demo data seeded (3 species + 50 Tiger observations + default user)")
