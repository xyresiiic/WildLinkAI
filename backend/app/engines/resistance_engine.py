"""
WildLink AI — Resistance Surface Engine

Generates a landscape resistance surface representing the relative
difficulty of wildlife movement through different landscape types.
"""
import logging
import numpy as np
from typing import Dict, List
from app.core.config import settings

logger = logging.getLogger("wildlink.resistance")


class ResistanceEngine:
    """
    Resistance Surface Engine.

    Creates a resistance raster where each cell has a value
    representing how difficult it is for wildlife to traverse.
    Low resistance = easy movement, high resistance = difficult/blocked.
    """

    # Configurable resistance values (0-100 scale)
    RESISTANCE_VALUES = {
        "dense_forest": 1,
        "moist_deciduous_forest": 3,
        "dry_deciduous_forest": 8,
        "open_forest": 12,
        "grassland": 20,
        "scrubland": 30,
        "water_body": 40,
        "agriculture": 60,
        "road_minor": 70,
        "road_major": 90,
        "settlement": 95,
        "barren": 50,
    }

    def __init__(self, project_id: str, db):
        self.project_id = project_id
        self.db = db

    async def run(self) -> np.ndarray:
        """Generate the resistance surface for the study region."""
        logger.info(f"Building resistance surface for project {self.project_id}")

        # Load project & species
        from sqlalchemy.orm import selectinload
        from app.models.models import Project, HabitatZone
        from sqlalchemy import select

        res = await self.db.execute(
            select(Project).options(selectinload(Project.species)).where(Project.id == self.project_id)
        )
        project = res.scalar_one_or_none()
        species = project.species if project else None

        # Determine bounds from habitat zones or defaults
        hz_res = await self.db.execute(
            select(HabitatZone).where(HabitatZone.project_id == self.project_id)
        )
        zones = hz_res.scalars().all()

        min_lat, max_lat = 22.0, 25.0
        min_lng, max_lng = 78.5, 82.5

        if zones:
            lats, lngs = [], []
            for z in zones:
                if z.geometry and isinstance(z.geometry, dict) and "coordinates" in z.geometry:
                    coords = z.geometry["coordinates"][0]
                    for pt in coords:
                        lngs.append(pt[0])
                        lats.append(pt[1])
            if lats and lngs:
                min_lat, max_lat = min(lats), max(lats)
                min_lng, max_lng = min(lngs), max(lngs)

        resolution = settings.DEFAULT_GRID_RESOLUTION
        n_rows = max(10, int(round((max_lat - min_lat) / resolution)))
        n_cols = max(10, int(round((max_lng - min_lng) / resolution)))

        resistance_grid = np.zeros((n_rows, n_cols))

        for row in range(n_rows):
            for col in range(n_cols):
                lat = min_lat + row * resolution + resolution / 2
                lng = min_lng + col * resolution + resolution / 2
                resistance_grid[row, col] = self._calculate_cell_resistance(lat, lng, species)

        # Store as project metadata
        self._resistance_grid = resistance_grid
        self._grid_meta = {
            "min_lat": min_lat, "max_lat": max_lat,
            "min_lng": min_lng, "max_lng": max_lng,
            "resolution": resolution,
            "n_rows": n_rows, "n_cols": n_cols,
        }

        logger.info(f"Resistance surface generated: {n_rows}x{n_cols}")
        return resistance_grid

    def get_resistance_grid(self):
        """Return the computed resistance grid and metadata."""
        return self._resistance_grid, self._grid_meta

    def _calculate_cell_resistance(self, lat: float, lng: float, species=None) -> float:
        """Calculate resistance for a single cell based on simulated landscape features."""
        prefs = species.habitat_preferences if species and species.habitat_preferences else {}

        # Base: forest coverage
        forest_cover = 0.5 + 0.3 * np.sin(lat * 8) * np.cos(lng * 6) + 0.2 * np.sin((lat + lng) * 12)
        forest_cover = max(0.0, min(1.0, forest_cover))

        # Check if species is grassland/scrubland specialist or aquatic
        is_grassland = (prefs.get("grassland", 0.5) + prefs.get("scrubland", 0.5)) > 1.2
        is_aquatic = prefs.get("water_body", 0.5) > 0.8

        if is_aquatic:
            base_resistance = 40.0
        elif is_grassland:
            base_resistance = 10 + forest_cover * 30  # open cover preferred
        else:
            base_resistance = 10 + (1 - forest_cover) * 50  # forest preferred

        # Road corridors add resistance
        road_resistance = self._road_resistance(lat, lng)

        # Settlement proximity
        settlement_resistance = self._settlement_resistance(lat, lng)

        # Protected areas reduce resistance
        pa_bonus = self._protected_area_bonus(lat, lng)

        # Water bodies
        water_resistance = self._water_resistance(lat, lng)
        if is_aquatic:
            # For gharial / aquatic, water body reduces resistance drastically!
            water_resistance = -25 * (water_resistance / 15.0)

        total = base_resistance + road_resistance + settlement_resistance + water_resistance - pa_bonus
        return max(1.0, min(100.0, total))

        # Clamp to [1, 100]
        return max(1.0, min(100.0, total))

    def _road_resistance(self, lat: float, lng: float) -> float:
        """Simulate road corridor resistance."""
        # National Highway approximations
        nh_proximity = min(
            abs(lat - 23.2),       # NH-7 east-west corridor
            abs(lng - 79.5) * 0.5,  # NH-44 north-south
        )
        return max(0, 30 * np.exp(-nh_proximity / 0.3))

    def _settlement_resistance(self, lat: float, lng: float) -> float:
        """Simulate settlement resistance."""
        cities = [
            (23.18, 79.95, 15),  # Jabalpur
            (21.15, 79.09, 12),  # Nagpur
            (23.26, 77.41, 12),  # Bhopal
            (23.83, 79.95, 8),   # Katni
            (22.07, 78.96, 6),   # Seoni
        ]
        max_resistance = 0
        for clat, clng, strength in cities:
            dist = np.sqrt((lat - clat) ** 2 + (lng - clng) ** 2)
            max_resistance = max(max_resistance, strength * np.exp(-dist / 0.15))
        return max_resistance

    def _protected_area_bonus(self, lat: float, lng: float) -> float:
        """Protected areas reduce resistance significantly."""
        reserves = [
            (23.5, 80.5, 0.3),    # Panna
            (22.85, 80.6, 0.25),  # Kanha
            (22.2, 78.1, 0.2),    # Pench
            (22.6, 77.7, 0.2),    # Satpura
            (23.8, 80.8, 0.15),   # Bandhavgarh
        ]
        max_bonus = 0
        for rlat, rlng, radius in reserves:
            dist = np.sqrt((lat - rlat) ** 2 + (lng - rlng) ** 2)
            if dist < radius:
                max_bonus = max(max_bonus, 30 * (1 - dist / radius))
        return max_bonus

    def _water_resistance(self, lat: float, lng: float) -> float:
        """Rivers add moderate resistance (crossable but difficult)."""
        river_proximity = max(
            np.exp(-((lat - 23.5) ** 2) / 0.02),
            np.exp(-((lng - 80.0) ** 2) / 0.03),
        )
        return 15 * river_proximity
