"""
===============================================================================
WildLink AI — API Routing Package (FastAPI Endpoints)
===============================================================================
Exposes RESTful API routers for the web client:
- species_router     — `/api/v1/species` (Catalog discovery & ecological profiles)
- projects_router    — `/api/v1/projects` (Project CRUD, dashboard metrics, GeoJSON export)
- analysis_router    — `/api/v1/analysis` (Pipeline background triggers & spatial layers)
- simulations_router — `/api/v1/simulations` (What-If counterfactual scenario evaluations)
"""

__title__ = "WildLink API Routes Package"
__description__ = "FastAPI HTTP routers and endpoint handlers"

from app.api.species_routes import router as species_router
from app.api.project_routes import router as projects_router
from app.api.analysis_routes import router as analysis_router
from app.api.simulation_routes import router as simulations_router

__all__ = [
    "species_router",
    "projects_router",
    "analysis_router",
    "simulations_router",
]
