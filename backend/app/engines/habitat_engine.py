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
from app.models import HabitatZone, Observation, Project, Species
from app.core import settings

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

            # Feature 3: Water proximity tailored to species ecology
            features["water_proximity"] = self._simulate_water_proximity(cell, species, obs_points)

            # Feature 4: Elevation suitability
            features["elevation_suitability"] = self._simulate_elevation(cell, species)

            # Feature 5: Human disturbance
            features["human_disturbance"] = self._simulate_human_disturbance(cell, species)

            # Feature 6: Protected area bonus
            features["protected_area"] = self._simulate_protected_area(cell, species, obs_points)

            # Feature 7: Road density
            features["road_density"] = self._simulate_road_density(cell, species)

            cell_with_features = {**cell, "features": features}
            featured_cells.append(cell_with_features)

        return featured_cells

    def _calculate_suitability(self, cells: List[dict], species) -> List[dict]:
        """Calculate habitat suitability score tailored to species ecological preferences."""
        prefs = (species.habitat_preferences if species and species.habitat_preferences else {})

        # Dynamic weights based on species ecology
        water_weight = 0.40 if prefs.get("water_body", 0.5) > 0.8 else 0.10
        grassland_pref = prefs.get("grassland", 0.5) + prefs.get("scrubland", 0.5)
        landcover_weight = 0.30 if grassland_pref > 1.2 else 0.25
        elevation_weight = 0.25 if (prefs.get("scrubland", 0.4) > 0.8 and prefs.get("dense_forest", 0.5) < 0.2) else 0.10
        obs_weight = 0.20
        pa_weight = 0.12
        disturbance_weight = -0.15 if prefs.get("settlement", 0.1) < 0.05 else -0.08

        total_pos = obs_weight + 0.08 + landcover_weight + water_weight + elevation_weight + pa_weight
        norm_factor = 1.0 / max(0.5, total_pos)

        for cell in cells:
            f = cell["features"]
            raw_score = (
                obs_weight * f["observation_proximity"]
                + 0.08 * f["observation_density"]
                + landcover_weight * f["landcover_suitability"]
                + water_weight * f["water_proximity"]
                + elevation_weight * f["elevation_suitability"]
                + pa_weight * f["protected_area"]
                + disturbance_weight * f["human_disturbance"]
                - 0.05 * f["road_density"]
            )
            # Normalized suitability with slight scaling for distinct high-quality core clusters
            score = max(0.08, min(0.98, raw_score * norm_factor * 1.3))
            cell["suitability_score"] = float(round(score, 4))

        return cells

    async def _store_results(self, cells: List[dict]):
        """Store habitat zones in the database."""
        # Clear old results
        await self.db.execute(
            delete(HabitatZone).where(HabitatZone.project_id == self.project_id)
        )

        # Only store cells with meaningful suitability (> threshold)
        threshold = settings.HABITAT_SUITABILITY_THRESHOLD * 0.7  # Store significant habitat zones
        filtered = [c for c in cells if c["suitability_score"] >= threshold]

        zones_to_add = []
        for cell in filtered:
            polygon = box(cell["min_lng"], cell["min_lat"], cell["max_lng"], cell["max_lat"])
            area_ha = self._estimate_area_hectares(cell)

            zone = HabitatZone(
                project_id=self.project_id,
                geometry=mapping(polygon),
                suitability_score=cell["suitability_score"],
                area_hectares=round(area_ha, 2),
                patch_id=cell["id"],
                fragmentation_level=self._classify_fragmentation(cell["suitability_score"]),
                metadata_=cell.get("features"),
            )
            zones_to_add.append(zone)

        self.db.add_all(zones_to_add)
        await self.db.flush()

    # ──────────────── Simulated Feature Functions ────────────────

    def _simulate_landcover(self, cell: dict, species=None) -> float:
        """Simulate land cover suitability based on species preferences and spatial patterns."""
        lat, lng = cell["lat"], cell["lng"]
        prefs = species.habitat_preferences if species and species.habitat_preferences else {}

        # Spatial vegetative heterogeneity
        veg_pattern = (
            0.5 + 0.3 * np.sin(lat * 8) * np.cos(lng * 6)
            + 0.2 * np.sin((lat + lng) * 12)
        )
        veg_pattern = max(0.0, min(1.0, veg_pattern))
        open_pattern = 1.0 - veg_pattern

        forest_pref = (prefs.get("dense_forest", 0.5) + prefs.get("moist_deciduous_forest", 0.5)) / 2.0
        open_pref = (prefs.get("grassland", 0.5) + prefs.get("scrubland", 0.5)) / 2.0

        if open_pref > forest_pref:
            suitability = open_pattern * 0.75 + veg_pattern * 0.25
        else:
            suitability = veg_pattern * 0.75 + open_pattern * 0.25

        return max(0.05, min(1.0, suitability))

    def _simulate_water_proximity(self, cell: dict, species=None, obs_points=None) -> float:
        """Simulate proximity to water bodies tailored to species ecology and regional river systems."""
        lat, lng = cell["lat"], cell["lng"]
        prefs = species.habitat_preferences if species and species.habitat_preferences else {}
        is_aquatic = prefs.get("water_body", 0.5) > 0.8

        if is_aquatic:
            # For Gharial (Chambal River Basin lat 25.5..27.5, lng 76.5..79.5):
            # Chambal river meanders from SW (Sawai Madhopur 25.9, 76.7) to NE (Etawah 26.8, 79.0)
            chambal_line_dist = abs((lat - 25.9) - (lng - 76.7) * 0.40)
            river_proximity = np.exp(-(chambal_line_dist ** 2) / 0.08)
            return float(min(1.0, max(0.2, river_proximity * 1.1)))

        if lat > 30.0:
            # Himalayan snow and glacial streams (Indus, Spiti, Zanskar)
            river_proximity = max(
                np.exp(-((lat - 34.15) ** 2 + (lng - 77.58) ** 2) / 0.5),  # Indus
                np.exp(-((lat - 32.25) ** 2 + (lng - 78.05) ** 2) / 0.3),  # Spiti
            )
            return float(min(1.0, river_proximity * 0.8 + 0.25))

        if lat < 15.0:
            # Western Ghats river systems (Kabini, Moyar, Bhavani)
            river_proximity = max(
                np.exp(-((lat - 11.95) ** 2 + (lng - 76.25) ** 2) / 0.2),  # Kabini
                np.exp(-((lat - 11.58) ** 2 + (lng - 76.85) ** 2) / 0.2),  # Moyar
            )
            return float(min(1.0, river_proximity * 0.85 + 0.3))

        # Central India river corridors (Narmada, Ken, Betwa, Son)
        river_proximity = max(
            0.8 * np.exp(-((lat - 23.5) ** 2) / 0.1),
            0.7 * np.exp(-((lng - 80.0) ** 2) / 0.2),
            0.6 * np.exp(-((lat - 24.0 + (lng - 80.0) * 0.3) ** 2) / 0.05),
        )
        return float(min(1.0, river_proximity + 0.2))

    def _simulate_elevation(self, cell: dict, species=None) -> float:
        """Simulate elevation suitability based on species habitat needs."""
        lat, lng = cell["lat"], cell["lng"]
        prefs = species.habitat_preferences if species and species.habitat_preferences else {}

        # Western Himalayas (Snow Leopard: Ladakh / Spiti high altitude 3500m-5500m)
        if lat > 30.0:
            # High elevation alpine ridges have highest suitability
            mountain_ridge = 0.5 + 0.4 * np.sin(lat * 6) * np.cos(lng * 4) + 0.2 * np.sin((lat + lng) * 8)
            return float(max(0.3, min(1.0, 0.4 + 0.6 * mountain_ridge)))

        # Desert / Grassland (Great Indian Bustard: flat semi-arid steppes)
        if (prefs.get("grassland", 0.5) > 0.8 and prefs.get("dense_forest", 0.5) < 0.1):
            flatness = 1.0 - 0.3 * abs(np.sin(lat * 4) * np.cos(lng * 4))
            return float(max(0.4, min(1.0, flatness)))

        # Aquatic (Gharial: low-elevation river channels and sandbars)
        if prefs.get("water_body", 0.5) > 0.8:
            return float(0.85)

        # Standard forest / hill terrain
        elev = 0.5 + 0.4 * np.sin(lat * 5) * np.cos(lng * 3)
        return float(max(0.2, min(1.0, elev)))

    def _simulate_human_disturbance(self, cell: dict, species=None) -> float:
        """Simulate human disturbance based on authentic regional towns and transport hubs."""
        lat, lng = cell["lat"], cell["lng"]

        if lat > 30.0:
            # Himalayas: Leh & Kaza
            leh = np.exp(-((lat - 34.15) ** 2 + (lng - 77.58) ** 2) / 0.08)
            kaza = np.exp(-((lat - 32.22) ** 2 + (lng - 78.07) ** 2) / 0.05)
            disturbance = 0.05 + 0.6 * max(leh, kaza)
            return float(min(1.0, disturbance))

        if lat < 15.0:
            # Western Ghats: Mysore, Gudalur, Ooty
            mysore = np.exp(-((lat - 12.30) ** 2 + (lng - 76.64) ** 2) / 0.1)
            ooty = np.exp(-((lat - 11.41) ** 2 + (lng - 76.70) ** 2) / 0.08)
            disturbance = 0.10 + 0.6 * max(mysore, ooty)
            return float(min(1.0, disturbance))

        if (lng < 73.0 and lat > 25.0):
            # Thar Desert: Jaisalmer, Pokhran, Barmer
            jaisalmer = np.exp(-((lat - 26.91) ** 2 + (lng - 70.91) ** 2) / 0.08)
            pokhran = np.exp(-((lat - 26.92) ** 2 + (lng - 71.92) ** 2) / 0.06)
            disturbance = 0.08 + 0.55 * max(jaisalmer, pokhran)
            return float(min(1.0, disturbance))

        if (lat > 25.5 and lat < 28.0 and lng > 76.5):
            # Chambal / Yamuna Basin: Morena, Dholpur, Agra, Etawah
            morena = np.exp(-((lat - 26.50) ** 2 + (lng - 78.00) ** 2) / 0.08)
            dholpur = np.exp(-((lat - 26.70) ** 2 + (lng - 77.90) ** 2) / 0.08)
            etawah = np.exp(-((lat - 26.78) ** 2 + (lng - 79.03) ** 2) / 0.08)
            disturbance = 0.12 + 0.55 * max(morena, dholpur, etawah)
            return float(min(1.0, disturbance))

        # Central India: Jabalpur, Nagpur, Bhopal
        jabalpur = np.exp(-((lat - 23.18) ** 2 + (lng - 79.95) ** 2) / 0.1)
        nagpur = np.exp(-((lat - 21.15) ** 2 + (lng - 79.09) ** 2) / 0.15)
        bhopal = np.exp(-((lat - 23.26) ** 2 + (lng - 77.41) ** 2) / 0.15)
        disturbance = 0.12 + 0.5 * max(jabalpur, nagpur, bhopal)
        return float(min(1.0, disturbance))

    def _simulate_protected_area(self, cell: dict, species=None, obs_points=None) -> float:
        """Simulate protected area presence from observation clusters and known sanctuaries."""
        lat, lng = cell["lat"], cell["lng"]

        # Universal: Proximity to core observation clusters acts as protected core
        if obs_points is not None and len(obs_points) > 0:
            cell_pt = np.array([lat, lng])
            dists = np.sqrt(np.sum((obs_points - cell_pt) ** 2, axis=1))
            min_dist = np.min(dists)
            if min_dist < 0.25:
                return float(1.0 - min_dist / 0.25)

        return 0.0

    def _simulate_road_density(self, cell: dict, species=None) -> float:
        """Simulate road density across regions."""
        lat, lng = cell["lat"], cell["lng"]
        # Regional highway corridor approximation
        highway = 0.2 + 0.25 * np.exp(-abs(np.sin(lat * 3) + np.cos(lng * 2)) / 0.4)
        return float(min(1.0, highway))

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
