"""
===============================================================================
WildLink AI — Analytical GIS Engines Package
===============================================================================
Provides the 6 core computational engines for conservation intelligence:
1. HabitatEngine      — Random Forest ecological suitability modeling [0..1]
2. FragmentationEngine — SciPy connected component patch morphology & metrics
3. ResistanceEngine    — Species-specific landscape cost-surface raster [1..100]
4. ConnectivityEngine  — Dijkstra least-cost corridors & NetworkX graph topology
5. PriorityEngine      — Multi-criteria weighted decision scoring & AI explainability
6. SimulationEngine    — What-If counterfactual scenario impact assessment
"""

__title__ = "WildLink GIS Engines Package"
__description__ = "Spatial ML algorithms and conservation connectivity engines"

from app.engines.habitat_engine import HabitatEngine
from app.engines.fragmentation_engine import FragmentationEngine
from app.engines.resistance_engine import ResistanceEngine
from app.engines.connectivity_engine import ConnectivityEngine
from app.engines.priority_engine import PriorityEngine
from app.engines.simulation_engine import SimulationEngine

__all__ = [
    "HabitatEngine",
    "FragmentationEngine",
    "ResistanceEngine",
    "ConnectivityEngine",
    "PriorityEngine",
    "SimulationEngine",
]
