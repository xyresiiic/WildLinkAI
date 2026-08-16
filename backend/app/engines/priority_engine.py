"""
WildLink AI — Priority Engine

Converts analytical outputs into conservation intervention rankings
using configurable weighted scoring with explainability.
"""
import logging
import numpy as np
from typing import Dict, List
from sqlalchemy import select, delete, update, func
from app.models import HabitatZone, Corridor, PriorityZone, Observation, EvidenceQuality
from shapely.geometry import box, shape, mapping
from app.core import settings

logger = logging.getLogger("wildlink.priority")


class PriorityEngine:
    """
    Priority Engine.

    Ranks potential conservation intervention zones using:
    Priority = w1(Habitat) + w2(Connectivity) + w3(Species) + w4(Restoration) - w5(Constraint)
    """

    def __init__(self, project_id: str, db):
        self.project_id = project_id
        self.db = db

        # Configurable weights
        self.weights = {
            "habitat": settings.WEIGHT_HABITAT,
            "connectivity": settings.WEIGHT_CONNECTIVITY,
            "species": settings.WEIGHT_SPECIES,
            "restoration": settings.WEIGHT_RESTORATION,
            "constraint": settings.WEIGHT_CONSTRAINT,
        }

    async def run(self) -> List[Dict]:
        """Run priority scoring on candidate zones."""
        logger.info(f"Running priority analysis for project {self.project_id}")

        # 1. Identify candidate zones (areas between high-value patches)
        candidates = await self._identify_candidate_zones()
        logger.info(f"Identified {len(candidates)} candidate zones")

        if not candidates:
            return []

        # 2. Score each candidate
        scored = self._score_candidates(candidates)

        # 3. Rank and classify
        ranked = self._rank_and_classify(scored)

        # 4. Generate explanations
        explained = self._generate_explanations(ranked)

        # 5. Store results
        await self._store_results(explained)

        logger.info(f"Priority analysis complete: {len(explained)} zones ranked")
        return explained

    async def _identify_candidate_zones(self) -> List[Dict]:
        """Identify candidate intervention zones from habitat and corridor data."""
        # Load habitat zones with moderate-to-high suitability
        result = await self.db.execute(
            select(HabitatZone)
            .where(
                HabitatZone.project_id == self.project_id,
                HabitatZone.suitability_score >= 0.3  # Include marginal areas as candidates
            )
        )
        zones = result.scalars().all()

        # Load corridors
        corridor_result = await self.db.execute(
            select(Corridor).where(Corridor.project_id == self.project_id)
        )
        corridors = corridor_result.scalars().all()

        # Pre-parse zone geometries once to avoid millions of redundant shapely conversions
        parsed_zones = []
        for zone in zones:
            try:
                z_shape = shape(zone.geometry) if isinstance(zone.geometry, dict) else None
                if z_shape:
                    parsed_zones.append((zone, z_shape, z_shape.centroid))
            except Exception:
                continue

        candidate_zone_ids = set()
        candidates = []

        # Strategy 1: Zones near corridor midpoints (high connectivity potential)
        for corridor in corridors:
            try:
                corridor_shape = shape(corridor.geometry) if isinstance(corridor.geometry, dict) else None
                if not corridor_shape:
                    continue
                midpoint = corridor_shape.interpolate(0.5, normalized=True)

                for zone, zone_shape, centroid in parsed_zones:
                    if zone.id in candidate_zone_ids:
                        continue
                    dist = midpoint.distance(centroid)
                    if dist < 0.1:  # Within ~11km
                        candidate_zone_ids.add(zone.id)
                        candidates.append({
                            "zone": zone,
                            "geometry": zone_shape,
                            "corridor_connectivity": corridor.connectivity_score or 0,
                            "corridor_resistance": corridor.resistance_score or 0,
                            "near_corridor": True,
                        })
            except Exception:
                continue

        # Strategy 2: High-suitability zones that are fragmented
        for zone, zone_shape, centroid in parsed_zones:
            if zone.id not in candidate_zone_ids and zone.suitability_score >= 0.45 and zone.fragmentation_level in ("medium", "high"):
                candidate_zone_ids.add(zone.id)
                candidates.append({
                    "zone": zone,
                    "geometry": zone_shape,
                    "corridor_connectivity": 0,
                    "corridor_resistance": 50,
                    "near_corridor": False,
                })

        # Strategy 3: Top core habitat zones (if fewer than 20 candidates selected)
        if len(candidates) < 20:
            sorted_zones = sorted(parsed_zones, key=lambda p: p[0].suitability_score or 0, reverse=True)
            for zone, zone_shape, centroid in sorted_zones:
                if zone.id not in candidate_zone_ids:
                    candidate_zone_ids.add(zone.id)
                    candidates.append({
                        "zone": zone,
                        "geometry": zone_shape,
                        "corridor_connectivity": 0,
                        "corridor_resistance": 40,
                        "near_corridor": False,
                    })
                if len(candidates) >= 50:
                    break

        # Limit to top candidates
        return candidates[:50]

    def _score_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """Score each candidate zone on all factors."""
        scored = []

        for candidate in candidates:
            zone = candidate["zone"]

            # Factor 1: Habitat value (0-100)
            habitat_score = zone.suitability_score * 100

            # Factor 2: Connectivity benefit (0-100)
            if candidate["near_corridor"]:
                connectivity_score = min(100, candidate["corridor_connectivity"] * 1.2)
            else:
                connectivity_score = max(0, 50 - candidate.get("corridor_resistance", 50) * 0.5)

            # Factor 3: Species relevance (0-100)
            # Based on proximity to observations and habitat preferences
            species_score = self._calculate_species_relevance(zone)

            # Factor 4: Restoration opportunity (0-100)
            # Higher for medium-suitability areas (not already perfect, not hopeless)
            restoration_score = self._calculate_restoration_opportunity(zone)

            # Factor 5: Constraints (0-100, subtracted)
            constraint_score = self._calculate_constraints(zone)

            # Weighted priority score
            priority = (
                self.weights["habitat"] * habitat_score
                + self.weights["connectivity"] * connectivity_score
                + self.weights["species"] * species_score
                + self.weights["restoration"] * restoration_score
                - self.weights["constraint"] * constraint_score
            )

            # Normalize to 0-100
            priority = max(0, min(100, priority))

            scored.append({
                **candidate,
                "priority_score": round(priority, 2),
                "habitat_score": round(habitat_score, 2),
                "connectivity_score": round(connectivity_score, 2),
                "species_score": round(species_score, 2),
                "restoration_score": round(restoration_score, 2),
                "constraint_score": round(constraint_score, 2),
            })

        return scored

    def _rank_and_classify(self, scored: List[Dict]) -> List[Dict]:
        """Rank zones and assign priority levels."""
        # Sort by priority score descending
        scored.sort(key=lambda x: x["priority_score"], reverse=True)

        # Ensure spatial variety while allowing rich priority selections (up to 4 zones per patch)
        patch_counts = {}
        unique = []
        for item in scored:
            patch_id = item["zone"].patch_id or 0
            count = patch_counts.get(patch_id, 0)
            if count < 4:
                patch_counts[patch_id] = count + 1
                unique.append(item)
            if len(unique) >= 20:
                break

        # Assign ranks and levels
        for rank, item in enumerate(unique, 1):
            item["rank"] = rank
            score = item["priority_score"]
            if score >= 75:
                item["priority_level"] = "critical"
            elif score >= 55:
                item["priority_level"] = "high"
            elif score >= 35:
                item["priority_level"] = "medium"
            else:
                item["priority_level"] = "low"

        return unique[:20]  # Top 20 zones

    def _generate_explanations(self, ranked: List[Dict]) -> List[Dict]:
        """Generate human-readable explanations for each zone's ranking."""
        for item in ranked:
            factors = {
                "habitat": item["habitat_score"],
                "connectivity": item["connectivity_score"],
                "species": item["species_score"],
                "restoration": item["restoration_score"],
            }

            # Find dominant factor
            dominant = max(factors, key=factors.get)
            item["dominant_factor"] = dominant

            # Generate explanation
            explanations = []
            if factors["connectivity"] > 60:
                explanations.append("connects high-value habitat patches with significant connectivity potential")
            if factors["habitat"] > 60:
                explanations.append("contains high-quality habitat suitable for the target species")
            if factors["species"] > 60:
                explanations.append("is near known species observations indicating active wildlife presence")
            if factors["restoration"] > 60:
                explanations.append("presents a strong restoration opportunity with moderate existing habitat")

            if not explanations:
                explanations.append("shows moderate conservation potential across multiple factors")

            item["explanation"] = (
                f"This zone is ranked #{item['rank']} because it "
                + ", and ".join(explanations)
                + f". The dominant contributing factor is {dominant} "
                + f"(score: {factors[dominant]:.0f}/100)."
            )

            # Evidence quality
            if item["habitat_score"] > 50 and item["species_score"] > 50:
                item["evidence_quality"] = EvidenceQuality.HIGH
            elif item["habitat_score"] > 30 or item["species_score"] > 30:
                item["evidence_quality"] = EvidenceQuality.MODERATE
            else:
                item["evidence_quality"] = EvidenceQuality.LOW

            # Recommended Action
            if dominant == "connectivity" and item.get("corridor_resistance", 0) > 30:
                item["recommended_action"] = "Construct Wildlife Overpass / Eco-duct across Transport Corridor"
            elif dominant == "restoration":
                item["recommended_action"] = "Targeted Reforestation & Native Vegetation Corridor Planting"
            elif dominant == "habitat":
                item["recommended_action"] = "Designate Protected Core Buffer & Enhance Anti-Poaching Patrols"
            else:
                item["recommended_action"] = "Community Conservation Reserve & Human-Wildlife Conflict Mitigation"

        return ranked

    async def _store_results(self, zones: List[Dict]):
        """Store priority zones in the database."""
        # Clear old priority zones
        await self.db.execute(
            delete(PriorityZone).where(PriorityZone.project_id == self.project_id)
        )

        for item in zones:
            zone = item["zone"]
            pz = PriorityZone(
                project_id=self.project_id,
                geometry=zone.geometry,
                rank=item["rank"],
                priority_score=item["priority_score"],
                priority_level=item["priority_level"],
                habitat_score=item["habitat_score"],
                connectivity_score=item["connectivity_score"],
                species_score=item["species_score"],
                restoration_score=item["restoration_score"],
                constraint_score=item["constraint_score"],
                dominant_factor=item["dominant_factor"],
                explanation=item["explanation"],
                evidence_quality=item["evidence_quality"],
                factors_json={
                    "habitat": item["habitat_score"],
                    "connectivity": item["connectivity_score"],
                    "species": item["species_score"],
                    "restoration": item["restoration_score"],
                    "constraint": item["constraint_score"],
                    "recommended_action": item.get("recommended_action", "Conservation Buffer"),
                    "weights": self.weights,
                },
                area_hectares=zone.area_hectares,
            )
            self.db.add(pz)

        await self.db.flush()

    # ──────────────── Factor Calculation Methods ────────────────

    def _calculate_species_relevance(self, zone) -> float:
        """Calculate species relevance score."""
        # Based on suitability and metadata
        base = zone.suitability_score * 80
        if zone.metadata_ and isinstance(zone.metadata_, dict):
            obs_prox = zone.metadata_.get("observation_proximity", 0)
            base += obs_prox * 20
        return min(100, base)

    def _calculate_restoration_opportunity(self, zone) -> float:
        """Calculate restoration opportunity."""
        s = zone.suitability_score
        # Best opportunity: moderate suitability (0.3-0.7)
        # Too high = already good, too low = too degraded
        if 0.3 <= s <= 0.7:
            return 60 + (0.5 - abs(s - 0.5)) * 80
        elif s > 0.7:
            return 30  # Already suitable, less restoration needed
        else:
            return 20 + s * 50  # Low but some potential

    def _calculate_constraints(self, zone) -> float:
        """Calculate constraint score (factors that make intervention harder)."""
        if zone.metadata_ and isinstance(zone.metadata_, dict):
            disturbance = zone.metadata_.get("human_disturbance", 0.3)
            road_density = zone.metadata_.get("road_density", 0.3)
            return (disturbance * 50 + road_density * 30)
        return 25  # Default moderate constraint
