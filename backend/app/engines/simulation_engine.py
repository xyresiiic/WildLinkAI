"""
WildLink AI — Simulation Engine

What-If Conservation Simulator.
Compares baseline connectivity with hypothetical restoration scenarios.
"""
import logging
import numpy as np
from typing import Dict, List, Optional
from sqlalchemy import select, update
from app.models.models import Simulation, Corridor, PriorityZone, HabitatZone
from app.core.config import settings

logger = logging.getLogger("wildlink.simulation")


class SimulationEngine:
    """
    Simulation Engine.

    Process:
    1. Load baseline connectivity model
    2. Apply hypothetical intervention (reduce resistance in target zone)
    3. Recalculate affected connectivity
    4. Compare with baseline
    """

    def __init__(self, project_id: str, simulation_id: str, db):
        self.project_id = project_id
        self.simulation_id = simulation_id
        self.db = db

    async def run(self) -> Dict:
        """Run the What-If simulation."""
        logger.info(f"Running simulation {self.simulation_id}")

        # 1. Load simulation parameters
        sim = await self._load_simulation()
        if not sim:
            raise ValueError("Simulation not found")

        # 2. Calculate baseline connectivity
        baseline = await self._calculate_baseline_connectivity()
        logger.info(f"Baseline connectivity: {baseline:.2f}")

        # 3. Identify intervention zones
        intervention_zones = await self._get_intervention_zones(sim)

        # 4. Simulate intervention effect
        simulated = self._simulate_intervention(baseline, intervention_zones, sim)
        logger.info(f"Simulated connectivity: {simulated:.2f}")

        # 5. Calculate improvement
        improvement = simulated - baseline
        pct_change = (improvement / max(0.01, baseline)) * 100

        result = {
            "baseline_connectivity": round(baseline, 2),
            "simulated_connectivity": round(simulated, 2),
            "improvement": round(improvement, 2),
            "percentage_change": round(pct_change, 2),
            "intervention_zones": [
                {
                    "zone_id": str(z.get("id", "")),
                    "rank": z.get("rank"),
                    "area_hectares": z.get("area_hectares"),
                    "habitat_improvement": round(z.get("habitat_improvement", 0), 2),
                    "connectivity_improvement": round(z.get("connectivity_improvement", 0), 2),
                }
                for z in intervention_zones
            ],
            "recommendation": self._generate_recommendation(
                baseline, simulated, improvement, intervention_zones
            ),
        }

        return result

    async def _load_simulation(self):
        """Load simulation from database."""
        result = await self.db.execute(
            select(Simulation).where(Simulation.id == self.simulation_id)
        )
        return result.scalar_one_or_none()

    async def _calculate_baseline_connectivity(self) -> float:
        """Calculate baseline connectivity score from existing corridors."""
        result = await self.db.execute(
            select(Corridor).where(Corridor.project_id == self.project_id)
        )
        corridors = result.scalars().all()

        if not corridors:
            return 0.0

        # Baseline = weighted average connectivity of all corridors
        scores = [c.connectivity_score or 0 for c in corridors]
        weights = [1.0 / max(1, c.resistance_score or 1) for c in corridors]

        if sum(weights) == 0:
            return np.mean(scores)

        return float(np.average(scores, weights=weights))

    async def _get_intervention_zones(self, sim) -> List[Dict]:
        """Load the zones targeted for intervention."""
        zones = []

        if sim.zone_ids:
            # Load specific priority zones by ID
            for zone_id in sim.zone_ids:
                result = await self.db.execute(
                    select(PriorityZone).where(PriorityZone.id == zone_id)
                )
                pz = result.scalar_one_or_none()
                if pz:
                    zones.append({
                        "id": pz.id,
                        "rank": pz.rank,
                        "priority_score": pz.priority_score,
                        "habitat_score": pz.habitat_score or 0,
                        "connectivity_score": pz.connectivity_score or 0,
                        "restoration_score": pz.restoration_score or 0,
                        "area_hectares": pz.area_hectares or 0,
                    })
        else:
            # Default: simulate restoring top 3 priority zones
            result = await self.db.execute(
                select(PriorityZone)
                .where(PriorityZone.project_id == self.project_id)
                .order_by(PriorityZone.rank)
                .limit(3)
            )
            for pz in result.scalars().all():
                zones.append({
                    "id": pz.id,
                    "rank": pz.rank,
                    "priority_score": pz.priority_score,
                    "habitat_score": pz.habitat_score or 0,
                    "connectivity_score": pz.connectivity_score or 0,
                    "restoration_score": pz.restoration_score or 0,
                    "area_hectares": pz.area_hectares or 0,
                })

        return zones

    def _simulate_intervention(
        self, baseline: float, zones: List[Dict], sim
    ) -> float:
        """
        Simulate the effect of conservation intervention on connectivity.

        Supports intervention types:
        - habitat_restoration: standard vegetation recovery
        - wildlife_crossing: highway overpass / eco-duct (high connectivity gain)
        - protected_area_expansion: core reserve designation
        - community_conservation: human-wildlife conflict reduction
        """
        if not zones:
            return baseline

        itype = getattr(sim, "intervention_type", "habitat_restoration") or "habitat_restoration"
        params = getattr(sim, "parameters", {}) or {}
        intensity = float(params.get("intensity", 1.0) if isinstance(params, dict) else 1.0)

        # Multipliers based on intervention strategy
        type_multipliers = {
            "habitat_restoration": {"conn": 0.40, "hab": 0.40, "scale": 0.16},
            "wildlife_crossing": {"conn": 0.65, "hab": 0.20, "scale": 0.22},
            "protected_area_expansion": {"conn": 0.35, "hab": 0.55, "scale": 0.18},
            "community_conservation": {"conn": 0.30, "hab": 0.40, "scale": 0.14},
        }
        weights = type_multipliers.get(itype, type_multipliers["habitat_restoration"])

        total_improvement = 0.0

        for zone in zones:
            restoration_potential = zone.get("restoration_score", 50) / 100.0
            connectivity_potential = zone.get("connectivity_score", 50) / 100.0
            area_factor = min(1.0, (zone.get("area_hectares", 100) / 1000.0))

            zone_eff = (
                restoration_potential * weights["hab"]
                + connectivity_potential * weights["conn"]
                + area_factor * 0.20
            ) * baseline * weights["scale"] * intensity

            zone["habitat_improvement"] = restoration_potential * 35 * intensity
            zone["connectivity_improvement"] = zone_eff
            total_improvement += zone_eff

        # Apply diminishing returns for multiple simultaneous zones
        if len(zones) > 1:
            total_improvement *= (1 - 0.08 * min(5, len(zones) - 1))

        return baseline + total_improvement

    def _generate_recommendation(
        self, baseline: float, simulated: float, improvement: float,
        zones: List[Dict]
    ) -> str:
        """Generate a recommendation based on simulation results."""
        if improvement <= 0:
            return (
                "The simulated intervention does not show a meaningful "
                "connectivity improvement under the current model assumptions. "
                "Consider alternative intervention zones or parameters."
            )

        pct = (improvement / max(0.01, baseline)) * 100

        if pct > 30:
            strength = "transformative"
        elif pct > 15:
            strength = "significant"
        elif pct > 5:
            strength = "moderate"
        else:
            strength = "modest"

        zone_desc = ", ".join(
            f"Zone #{z.get('rank', '?')}" for z in zones[:3]
        )

        return (
            f"Implementing intervention in {zone_desc} yields a {strength} estimated connectivity "
            f"gain of +{improvement:.1f} points (+{pct:.1f}% net improvement). "
            f"This intervention creates a vital ecological stepping stone, connecting fragmented patches "
            f"and mitigating resistance barriers across the landscape."
        )
