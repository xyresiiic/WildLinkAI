"""
WildLink AI — Fragmentation Engine

Identifies isolated habitat patches using connected component analysis
on the suitability grid. Calculates patch metrics.
"""
import logging
import numpy as np
from typing import List, Dict
from scipy import ndimage
from shapely.geometry import box, MultiPolygon, mapping
from shapely.ops import unary_union
from sqlalchemy import select, update, delete
from app.models.models import HabitatZone
from app.core.config import settings

logger = logging.getLogger("wildlink.fragmentation")


class FragmentationEngine:
    """
    Fragmentation Engine.

    Converts habitat suitability data into distinct habitat patches,
    calculates patch metrics, and identifies fragmentation levels.
    """

    def __init__(self, project_id: str, db):
        self.project_id = project_id
        self.db = db
        self.threshold = settings.HABITAT_SUITABILITY_THRESHOLD

    async def run(self) -> Dict:
        """Run fragmentation analysis on existing habitat zones."""
        logger.info(f"Running fragmentation analysis for project {self.project_id}")

        # 1. Load habitat zones
        zones = await self._load_habitat_zones()
        if not zones:
            logger.warning("No habitat zones found for fragmentation analysis")
            return {"patches": 0}

        logger.info(f"Loaded {len(zones)} habitat zones")

        # 2. Build suitability grid
        grid, grid_meta = self._build_grid(zones)

        # 3. Threshold to binary
        binary_grid = (grid >= self.threshold).astype(int)

        # 4. Connected component analysis
        labeled_grid, num_patches = ndimage.label(binary_grid)
        logger.info(f"Found {num_patches} habitat patches")

        # 5. Calculate patch metrics
        patch_metrics = self._calculate_patch_metrics(labeled_grid, grid, grid_meta, num_patches)

        # 6. Update habitat zones with patch IDs and metrics
        await self._update_zones_with_patches(zones, labeled_grid, grid_meta, patch_metrics)

        result = {
            "total_patches": num_patches,
            "patch_metrics": patch_metrics,
            "fragmentation_index": self._calculate_fragmentation_index(patch_metrics),
        }

        logger.info(f"Fragmentation analysis complete: {num_patches} patches identified")
        return result

    async def _load_habitat_zones(self) -> List:
        """Load existing habitat zones."""
        result = await self.db.execute(
            select(HabitatZone)
            .where(HabitatZone.project_id == self.project_id)
            .order_by(HabitatZone.patch_id)
        )
        return result.scalars().all()

    def _build_grid(self, zones) -> tuple:
        """Build a 2D numpy grid from habitat zones."""
        # Determine grid bounds
        lats = []
        lngs = []
        scores = {}

        for zone in zones:
            if zone.metadata_:
                # Use patch_id to reconstruct grid position
                pass
            # Use suitability_score directly
            scores[zone.patch_id] = zone.suitability_score

        # Build from known grid
        resolution = settings.DEFAULT_GRID_RESOLUTION
        min_lat, max_lat = 22.0, 25.0
        min_lng, max_lng = 78.5, 82.5

        n_rows = int((max_lat - min_lat) / resolution)
        n_cols = int((max_lng - min_lng) / resolution)

        grid = np.zeros((n_rows, n_cols))
        grid_meta = {
            "min_lat": min_lat, "max_lat": max_lat,
            "min_lng": min_lng, "max_lng": max_lng,
            "resolution": resolution,
            "n_rows": n_rows, "n_cols": n_cols,
        }

        # Fill grid from zones
        for zone in zones:
            if zone.patch_id is not None:
                row = zone.patch_id // n_cols
                col = zone.patch_id % n_cols
                if 0 <= row < n_rows and 0 <= col < n_cols:
                    grid[row, col] = zone.suitability_score

        return grid, grid_meta

    def _calculate_patch_metrics(
        self, labeled_grid: np.ndarray, suitability_grid: np.ndarray,
        grid_meta: dict, num_patches: int
    ) -> List[dict]:
        """Calculate metrics for each habitat patch."""
        resolution = grid_meta["resolution"]
        metrics = []

        # Get patch centroids for distance calculations
        centroids = ndimage.center_of_mass(labeled_grid > 0, labeled_grid, range(1, num_patches + 1))

        for patch_id in range(1, num_patches + 1):
            mask = labeled_grid == patch_id
            pixel_count = np.sum(mask)

            if pixel_count == 0:
                continue

            # Area (approximate)
            cell_area_ha = (resolution * 111.0) ** 2 * 100  # rough hectares per cell
            area_ha = pixel_count * cell_area_ha

            # Average suitability
            avg_suitability = float(np.mean(suitability_grid[mask]))

            # Compactness (ratio of area to perimeter²)
            # Simple: count edge pixels
            eroded = ndimage.binary_erosion(mask)
            perimeter_pixels = np.sum(mask) - np.sum(eroded)
            compactness = pixel_count / max(1, (perimeter_pixels ** 2)) * 100

            # Distance to nearest other patch
            min_distance = float("inf")
            if len(centroids) > 1:
                current_centroid = centroids[patch_id - 1]
                for other_id in range(num_patches):
                    if other_id != patch_id - 1:
                        dist = np.sqrt(
                            (current_centroid[0] - centroids[other_id][0]) ** 2
                            + (current_centroid[1] - centroids[other_id][1]) ** 2
                        )
                        min_distance = min(min_distance, dist)

            nearest_km = min_distance * resolution * 111.0 if min_distance < float("inf") else None

            metrics.append({
                "patch_id": patch_id,
                "pixel_count": int(pixel_count),
                "area_hectares": round(area_ha, 1),
                "avg_suitability": round(avg_suitability, 4),
                "compactness": round(compactness, 4),
                "nearest_patch_distance_km": round(nearest_km, 2) if nearest_km else None,
                "centroid_row": centroids[patch_id - 1][0],
                "centroid_col": centroids[patch_id - 1][1],
            })

        return metrics

    async def _update_zones_with_patches(
        self, zones, labeled_grid, grid_meta, patch_metrics
    ):
        """Update habitat zones with connected component patch IDs."""
        n_cols = grid_meta["n_cols"]
        n_rows = grid_meta["n_rows"]

        # Build a lookup from patch_metrics
        patch_lookup = {pm["patch_id"]: pm for pm in patch_metrics}

        for zone in zones:
            if zone.patch_id is not None:
                row = zone.patch_id // n_cols
                col = zone.patch_id % n_cols
                if 0 <= row < n_rows and 0 <= col < n_cols:
                    component_id = int(labeled_grid[row, col])
                    if component_id > 0 and component_id in patch_lookup:
                        pm = patch_lookup[component_id]
                        zone.patch_id = component_id
                        zone.nearest_patch_distance_km = pm.get("nearest_patch_distance_km")
                        zone.fragmentation_level = self._classify_fragmentation(pm)

        await self.db.flush()

    def _classify_fragmentation(self, patch_metric: dict) -> str:
        """Classify fragmentation level for a patch."""
        area = patch_metric.get("area_hectares", 0)
        distance = patch_metric.get("nearest_patch_distance_km", 0)

        if area > 5000 and (distance is None or distance < 5):
            return "low"
        elif area > 1000 and (distance is None or distance < 15):
            return "medium"
        else:
            return "high"

    def _calculate_fragmentation_index(self, patch_metrics: List[dict]) -> float:
        """Calculate an overall fragmentation index for the landscape."""
        if not patch_metrics:
            return 0.0

        # Based on number of patches, their sizes, and distances
        n_patches = len(patch_metrics)
        avg_area = np.mean([pm["area_hectares"] for pm in patch_metrics])
        max_area = max(pm["area_hectares"] for pm in patch_metrics)

        # Higher fragmentation = more patches, smaller average, greater dispersion
        # Normalize to 0-100 scale
        fragmentation = min(100, (n_patches * 5) + (1000 / max(1, avg_area)) * 10)
        return round(fragmentation, 1)
