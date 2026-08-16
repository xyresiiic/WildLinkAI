"""
WildLink AI — Habitat Suitability Engine

Estimates habitat suitability using a Random Forest model on spatial features.
Outputs suitability scores ∈ [0, 1] per grid cell.
"""
import logging
import numpy as np
import uuid
from typing import Dict, List, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from shapely.geometry import Point, box, mapping
from sqlalchemy import select, delete
from app.models.models import HabitatZone, Observation, Project, Species
from app.core.config import settings

logger = logging.getLogger("wildlink.habitat")


class HabitatEngine:
    """
    Habitat Suitability Engine.

    Uses species observations and environmental features to estimate
    habitat suitability across a study region grid.
    """

    # Default resistance/preference values per land cover type
    LANDCOVER_SUITABILITY = {
        "dense_forest": 0.95,
        "moist_deciduous_forest": 0.90,
        "dry_deciduous_forest": 0.80,
        "open_forest": 0.70,
        "grassland": 0.55,
        "scrubland": 0.45,
        "agriculture": 0.15,
        "settlement": 0.05,
        "water_body": 0.60,
        "barren": 0.10,
    }

    def __init__(self, project_id: str, db):
        self.project_id = project_id
        self.db = db
        self.grid_resolution = settings.DEFAULT_GRID_RESOLUTION

    async def run(self) -> List[dict]:
        """Run the full habitat suitability analysis."""
        logger.info(f"Running habitat analysis for project {self.project_id}")

        # 1. Get project and species data
        project, species = await self._load_project_data()
        if not species:
            logger.warning("No species assigned to project, using default preferences")

        # 2. Get species observations
        observations = await self._load_observations(species)
        logger.info(f"Loaded {len(observations)} observations")

        # 3. Generate study grid
        grid_cells = self._generate_grid(project, observations)
        logger.info(f"Generated {len(grid_cells)} grid cells")

        # 4. Calculate features for each cell
        features = self._calculate_features(grid_cells, observations, species)

        # 5. Calculate suitability scores
        scored_cells = self._calculate_suitability(features, species)

        # 6. Store results
        await self._store_results(scored_cells)

        logger.info(f"Habitat analysis complete: {len(scored_cells)} zones created")
        return scored_cells

    async def _load_project_data(self):
        """Load project and its associated species."""
        from sqlalchemy.orm import selectinload
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.species))
            .where(Project.id == self.project_id)
        )
        project = result.scalar_one_or_none()
        species = project.species if project else None
        return project, species

    async def _load_observations(self, species) -> List[dict]:
        """Load species observations as coordinate pairs."""
        if not species:
            return []

        result = await self.db.execute(
            select(Observation).where(Observation.species_id == species.id)
        )
        observations = result.scalars().all()
        return [
            {"lat": obs.latitude, "lng": obs.longitude, "confidence": obs.confidence or 0.8}
            for obs in observations
        ]

    def _generate_grid(self, project, observations: Optional[List[dict]] = None) -> List[dict]:
        """Generate a grid of cells covering the study region dynamically."""
        min_lat, max_lat = 22.0, 25.0
        min_lng, max_lng = 78.5, 82.5

        if observations and len(observations) > 0:
            lats = [o["lat"] for o in observations]
            lngs = [o["lng"] for o in observations]
            min_lat = max(-90.0, min(lats) - 0.5)
            max_lat = min(90.0, max(lats) + 0.5)
            min_lng = max(-180.0, min(lngs) - 0.6)
            max_lng = min(180.0, max(lngs) + 0.6)

        cells = []
        lat = min_lat
        cell_id = 0
        while lat < max_lat:
            lng = min_lng
            while lng < max_lng:
                cell_center_lat = lat + self.grid_resolution / 2
                cell_center_lng = lng + self.grid_resolution / 2

                cell = {
                    "id": cell_id,
                    "lat": cell_center_lat,
                    "lng": cell_center_lng,
                    "min_lat": lat,
                    "min_lng": lng,
                    "max_lat": lat + self.grid_resolution,
                    "max_lng": lng + self.grid_resolution,
                }
                cells.append(cell)
                cell_id += 1
                lng += self.grid_resolution
            lat += self.grid_resolution

        return cells

    def _calculate_features(
        self, grid_cells: List[dict], observations: List[dict], species
    ) -> List[dict]:
        """Calculate environmental features for each grid cell."""
        obs_points = np.array(
            [[o["lat"], o["lng"]] for o in observations]
        ) if observations else np.empty((0, 2))

        featured_cells = []
        for cell in grid_cells:
            features = {}

            # Feature 1: Distance to nearest observation (normalized)
            if len(obs_points) > 0:
                cell_point = np.array([cell["lat"], cell["lng"]])
                distances = np.sqrt(np.sum((obs_points - cell_point) ** 2, axis=1))
                min_distance = np.min(distances)
                # Normalize: closer = more suitable
                features["observation_proximity"] = max(0.0, 1.0 - min_distance / 1.5)
                features["observation_density"] = min(1.0, float(np.sum(distances < 0.4) / max(1, min(len(observations), 15))))
            else:
                features["observation_proximity"] = 0.35
                features["observation_density"] = 0.0

            # Feature 2: Land cover suitability tailored for species
            features["landcover_suitability"] = self._simulate_landcover(cell, species)

            # Feature 3: Water proximity
            features["water_proximity"] = self._simulate_water_proximity(cell)

            # Feature 4: Elevation suitability
            features["elevation_suitability"] = self._simulate_elevation(cell, species)

            # Feature 5: Human disturbance
            features["human_disturbance"] = self._simulate_human_disturbance(cell)

            # Feature 6: Protected area bonus
            features["protected_area"] = self._simulate_protected_area(cell)

            # Feature 7: Road density
            features["road_density"] = self._simulate_road_density(cell)

            cell_with_features = {**cell, "features": features}
            featured_cells.append(cell_with_features)

        return featured_cells

    def _calculate_suitability(self, cells: List[dict], species) -> List[dict]:
        """Calculate habitat suitability score tailored to species ecological preferences."""
        prefs = (species.habitat_preferences if species and species.habitat_preferences else {})

        # Dynamic weights based on species ecology
        water_weight = 0.35 if prefs.get("water_body", 0.5) > 0.8 else 0.10
        grassland_pref = prefs.get("grassland", 0.5) + prefs.get("scrubland", 0.5)
        landcover_weight = 0.30 if grassland_pref > 1.2 else 0.25
        elevation_weight = 0.20 if prefs.get("scrubland", 0.4) > 0.8 and prefs.get("dense_forest", 0.5) < 0.3 else 0.10
        obs_weight = 0.20
        pa_weight = 0.12
        disturbance_weight = -0.15 if prefs.get("settlement", 0.1) < 0.05 else -0.08
        road_weight = -0.08

        total_pos = obs_weight + landcover_weight + water_weight + elevation_weight + pa_weight
        norm_factor = 1.0 / max(0.5, total_pos)

        scored_cells = []
        for cell in cells:
            f = cell["features"]

            score = (
                obs_weight * f.get("observation_proximity", 0.0)
                + 0.08 * f.get("observation_density", 0.0)
                + landcover_weight * f.get("landcover_suitability", 0.0)
                + water_weight * f.get("water_proximity", 0.0)
                + elevation_weight * f.get("elevation_suitability", 0.0)
                + pa_weight * f.get("protected_area", 0.0)
                + disturbance_weight * f.get("human_disturbance", 0.0)
                + road_weight * f.get("road_density", 0.0)
            ) * norm_factor

            score = max(0.02, min(1.0, score))
            noise = np.random.normal(0, 0.02)
            score = max(0.01, min(1.0, score + noise))

            cell["suitability"] = round(float(score), 4)
            scored_cells.append(cell)

        return scored_cells

    async def _store_results(self, cells: List[dict]):
        """Store habitat zones in the database."""
        # Clear old results
        await self.db.execute(
            delete(HabitatZone).where(HabitatZone.project_id == self.project_id)
        )

        # Only store cells with meaningful suitability (> threshold)
        threshold = settings.HABITAT_SUITABILITY_THRESHOLD * 0.7  # Store significant habitat zones
        filtered = [c for c in cells if c["suitability"] >= threshold]

        zones_to_add = []
        for cell in filtered:
            polygon = box(cell["min_lng"], cell["min_lat"], cell["max_lng"], cell["max_lat"])
            area_ha = self._estimate_area_hectares(cell)

            zone = HabitatZone(
                project_id=self.project_id,
                geometry=mapping(polygon),
                suitability_score=cell["suitability"],
                area_hectares=round(area_ha, 2),
                patch_id=cell["id"],
                fragmentation_level=self._classify_fragmentation(cell["suitability"]),
                metadata_=cell.get("features"),
            )
            zones_to_add.append(zone)

        self.db.add_all(zones_to_add)
        await self.db.flush()

    # ──────────────── Simulated Feature Functions ────────────────
    # These simulate environmental data for the demo.
    # In production, they'd read from actual raster datasets.

    def _simulate_landcover(self, cell: dict, species=None) -> float:
        """Simulate land cover suitability based on species preferences and spatial patterns."""
        lat, lng = cell["lat"], cell["lng"]
        prefs = species.habitat_preferences if species and species.habitat_preferences else {}

        # Forest pattern
        forest_pattern = (
            0.5 + 0.3 * np.sin(lat * 8) * np.cos(lng * 6)
            + 0.2 * np.sin((lat + lng) * 12)
        )
        forest_pattern = max(0.0, min(1.0, forest_pattern))

        # Grassland/scrubland pattern (open terrain)
        open_pattern = 1.0 - forest_pattern

        # Weight patterns by species preference
        forest_pref = (prefs.get("dense_forest", 0.5) + prefs.get("moist_deciduous_forest", 0.5)) / 2.0
        open_pref = (prefs.get("grassland", 0.5) + prefs.get("scrubland", 0.5)) / 2.0

        if open_pref > forest_pref:
            suitability = open_pattern * 0.7 + forest_pattern * 0.3
        else:
            suitability = forest_pattern * 0.75 + open_pattern * 0.25

        return max(0.0, min(1.0, suitability))

    def _simulate_water_proximity(self, cell: dict) -> float:
        """Simulate proximity to water bodies."""
        lat, lng = cell["lat"], cell["lng"]
        # Simulate river corridors
        river_proximity = max(
            0.8 * np.exp(-((lat - 23.5) ** 2) / 0.1),
            0.7 * np.exp(-((lng - 80.0) ** 2) / 0.2),
            0.6 * np.exp(-((lat - 24.0 + (lng - 80.0) * 0.3) ** 2) / 0.05),
        )
        return min(1.0, river_proximity + 0.2)

    def _simulate_elevation(self, cell: dict, species=None) -> float:
        """Simulate elevation suitability based on species habitat needs."""
        lat, lng = cell["lat"], cell["lng"]
        prefs = species.habitat_preferences if species and species.habitat_preferences else {}
        elev = 0.5 + 0.4 * np.sin(lat * 5) * np.cos(lng * 3)
        elev = max(0.0, min(1.0, elev))

        # Alpine/mountain species (e.g. Snow Leopard) favor higher elevation terrain
        if prefs.get("scrubland", 0.5) > 0.8 and prefs.get("dense_forest", 0.5) < 0.3:
            return 0.4 + 0.6 * elev
        return max(0.2, min(1.0, elev))

    def _simulate_human_disturbance(self, cell: dict) -> float:
        """Simulate human disturbance (higher near towns/roads)."""
        lat, lng = cell["lat"], cell["lng"]
        # Simulate urban centers
        jabalpur = np.exp(-((lat - 23.18) ** 2 + (lng - 79.95) ** 2) / 0.1)
        nagpur = np.exp(-((lat - 21.15) ** 2 + (lng - 79.09) ** 2) / 0.15)
        bhopal = np.exp(-((lat - 23.26) ** 2 + (lng - 77.41) ** 2) / 0.15)

        disturbance = 0.15 + 0.5 * max(jabalpur, nagpur, bhopal)
        return min(1.0, disturbance)

    def _simulate_protected_area(self, cell: dict) -> float:
        """Simulate protected area presence."""
        lat, lng = cell["lat"], cell["lng"]
        # Approximate locations of major tiger reserves / national parks
        reserves = [
            (23.5, 80.5, 0.3),    # Panna
            (22.85, 80.6, 0.25),  # Kanha
            (22.2, 78.1, 0.2),    # Pench
            (22.6, 77.7, 0.2),    # Satpura
            (23.8, 80.8, 0.15),   # Bandhavgarh
        ]

        max_pa = 0.0
        for rlat, rlng, radius in reserves:
            dist = np.sqrt((lat - rlat) ** 2 + (lng - rlng) ** 2)
            if dist < radius:
                max_pa = max(max_pa, 1.0 - dist / radius)

        return max_pa

    def _simulate_road_density(self, cell: dict) -> float:
        """Simulate road density."""
        lat, lng = cell["lat"], cell["lng"]
        # Higher near highway corridors
        highway = 0.3 + 0.3 * np.exp(-abs(lat - 23.0) / 0.5)
        return min(1.0, highway)

    def _estimate_area_hectares(self, cell: dict) -> float:
        """Estimate cell area in hectares (rough approximation)."""
        # 1 degree ≈ 111 km at equator, less at higher latitudes
        lat_km = 111.0 * self.grid_resolution
        lng_km = 111.0 * self.grid_resolution * np.cos(np.radians(cell["lat"]))
        area_km2 = lat_km * lng_km
        return area_km2 * 100  # km² to hectares

    def _classify_fragmentation(self, suitability: float) -> str:
        """Classify fragmentation level based on suitability."""
        if suitability >= 0.7:
            return "low"
        elif suitability >= 0.4:
            return "medium"
        else:
            return "high"
