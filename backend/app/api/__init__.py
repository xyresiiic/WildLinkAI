"""
WildLink AI — API Routing Package
Provides RESTful FastAPI routers for species, projects, spatial analysis, and What-If simulations.
"""
from app.api.species import router as species_router
from app.api.projects import router as projects_router
from app.api.analysis import router as analysis_router
from app.api.simulations import router as simulations_router

__all__ = [
    "species_router",
    "projects_router",
    "analysis_router",
    "simulations_router",
]
