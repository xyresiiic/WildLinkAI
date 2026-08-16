"""
WildLink AI — API Routing Package
Provides RESTful FastAPI routers for species, projects, spatial analysis, and What-If simulations.
"""
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
