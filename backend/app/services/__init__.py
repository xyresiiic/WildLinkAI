"""
===============================================================================
WildLink AI — Services Package (Background Workers & Pipelines)
===============================================================================
Coordinates asynchronous background tasks and pipeline orchestration:
- run_full_analysis — End-to-end 5-stage analytical pipeline execution
- run_simulation    — What-If counterfactual scenario impact calculation
"""

__title__ = "WildLink Services Package"
__description__ = "Background worker services and workflow orchestration"

from app.services.analysis_service import run_full_analysis
from app.services.simulation_service import run_simulation

__all__ = [
    "run_full_analysis",
    "run_simulation",
]
