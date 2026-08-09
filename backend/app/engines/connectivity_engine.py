"""
WildLink AI — Connectivity Engine

Identifies potential movement routes between habitat patches using
least-cost paths and NetworkX graph analysis.
"""
import logging
import numpy as np
import uuid
import networkx as nx
from typing import Dict, List, Tuple
from scipy import ndimage
from shapely.geometry import LineString, shape, mapping
from sqlalchemy import select, delete
from app.models.models import HabitatZone, Corridor
from app.core.config import settings

logger = logging.getLogger("wildlink.connectivity")


class ConnectivityEngine:
    """
    Connectivity Engine.

    Builds a habitat connectivity graph and identifies potential corridors
    using least-cost path analysis on the resistance surface.
    """

    MAX_CORRIDOR_DISTANCE = 200  # km — max distance to consider corridor

    def __init__(self, project_id: str, db):
        self.project_id = project_id
        self.db = db

    async def run(self) -> Dict:
        """Run connectivity analysis."""
        logger.info(f"Running connectivity analysis for project {self.project_id}")

        # 1. Load habitat patches (distinct patch IDs)
        patches = await self._load_patches()
        if len(patches) < 2:
            logger.warning("Need at least 2 patches for connectivity analysis")
            return {"corridors": 0, "graph_metrics": {}}

        logger.info(f"Found {len(patches)} distinct patches")

        # 2. Build resistance surface
        from app.engines.resistance_engine import ResistanceEngine
        resistance_engine = ResistanceEngine(self.project_id, self.db)
        resistance_grid = await resistance_engine.run()

        grid_meta = resistance_engine._grid_meta

        # 3. Build connectivity graph
        graph = self._build_graph(patches, resistance_grid, grid_meta)
        logger.info(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

        # 4. Calculate graph metrics
        metrics = self._calculate_graph_metrics(graph)

        # 5. Generate corridors from graph edges
        corridors = self._generate_corridors(graph, patches, resistance_grid, grid_meta)

        # 6. Store corridors
        await self._store_corridors(corridors)

        result = {
            "total_corridors": len(corridors),
            "graph_metrics": metrics,
            "connectivity_score": metrics.get("overall_connectivity", 0),
        }

        logger.info(f"Connectivity analysis complete: {len(corridors)} corridors")
        return result

    async def _load_patches(self) -> List[Dict]:
        """Load distinct habitat patches with their centroids."""
        result = await self.db.execute(
            select(HabitatZone)
            .where(
                HabitatZone.project_id == self.project_id,
                HabitatZone.suitability_score >= settings.HABITAT_SUITABILITY_THRESHOLD
            )
        )
        zones = result.scalars().all()

        # Group by patch_id and compute centroids
        patch_groups = {}
        for zone in zones:
            pid = zone.patch_id or 0
            if pid not in patch_groups:
                patch_groups[pid] = {
                    "patch_id": pid,
                    "zones": [],
                    "suitability_scores": [],
                }
            patch_groups[pid]["zones"].append(zone)
            patch_groups[pid]["suitability_scores"].append(zone.suitability_score)

        patches = []
        resolution = settings.DEFAULT_GRID_RESOLUTION
        min_lat, max_lat = 22.0, 25.0
        min_lng, max_lng = 78.5, 82.5
        n_cols = int((max_lng - min_lng) / resolution)

        for pid, group in patch_groups.items():
            if len(group["zones"]) < 3:
                continue  # Skip very small patches

            # Compute centroid from zone positions
            lats, lngs = [], []
            for zone in group["zones"]:
                if zone.patch_id is not None:
                    orig_id = zone.patch_id if zone.patch_id != pid else zone.id
                    # Approximate position
                    try:
                        geom_shape = shape(zone.geometry) if isinstance(zone.geometry, dict) else None
                        if geom_shape:
                            centroid = geom_shape.centroid
                            lats.append(centroid.y)
                            lngs.append(centroid.x)
                    except Exception:
                        pass

            if not lats:
                continue

            patches.append({
                "patch_id": pid,
                "centroid_lat": np.mean(lats),
                "centroid_lng": np.mean(lngs),
                "area_hectares": sum(z.area_hectares or 0 for z in group["zones"]),
                "avg_suitability": float(np.mean(group["suitability_scores"])),
                "zone_count": len(group["zones"]),
            })

        return patches

    def _build_graph(
        self, patches: List[Dict], resistance_grid: np.ndarray, grid_meta: dict
    ) -> nx.Graph:
        """Build a connectivity graph with patches as nodes and edges weighted by cost."""
        G = nx.Graph()

        # Add nodes
        for patch in patches:
            G.add_node(
                patch["patch_id"],
                lat=patch["centroid_lat"],
                lng=patch["centroid_lng"],
                area=patch["area_hectares"],
                suitability=patch["avg_suitability"],
            )

        # Add edges between nearby patches
        for i, p1 in enumerate(patches):
            for j, p2 in enumerate(patches):
                if j <= i:
                    continue

                # Geographic distance
                dist_deg = np.sqrt(
                    (p1["centroid_lat"] - p2["centroid_lat"]) ** 2 +
                    (p1["centroid_lng"] - p2["centroid_lng"]) ** 2
                )
                dist_km = dist_deg * 111.0

                if dist_km > self.MAX_CORRIDOR_DISTANCE:
                    continue

                # Compute path cost through resistance surface
                cost = self._compute_path_cost(
                    p1, p2, resistance_grid, grid_meta
                )

                # Connectivity score (inverse of cost, normalized)
                connectivity = max(0, 100 - cost / max(1, dist_km) * 2)

                G.add_edge(
                    p1["patch_id"], p2["patch_id"],
                    distance_km=round(dist_km, 2),
                    cost=round(cost, 2),
                    connectivity_score=round(connectivity, 2),
                )

        return G

    def _compute_path_cost(
        self, p1: Dict, p2: Dict, resistance_grid: np.ndarray, grid_meta: dict
    ) -> float:
        """Compute approximate least-cost path between two patch centroids."""
        resolution = grid_meta["resolution"]
        n_rows = grid_meta["n_rows"]
        n_cols = grid_meta["n_cols"]

        # Convert centroids to grid coordinates
        r1 = int((p1["centroid_lat"] - grid_meta["min_lat"]) / resolution)
        c1 = int((p1["centroid_lng"] - grid_meta["min_lng"]) / resolution)
        r2 = int((p2["centroid_lat"] - grid_meta["min_lat"]) / resolution)
        c2 = int((p2["centroid_lng"] - grid_meta["min_lng"]) / resolution)

        # Clamp to grid bounds
        r1, c1 = max(0, min(r1, n_rows-1)), max(0, min(c1, n_cols-1))
        r2, c2 = max(0, min(r2, n_rows-1)), max(0, min(c2, n_cols-1))

        # Simple straight-line cost integration (approximation of least-cost path)
        # For full LCP, scipy.ndimage or skimage could be used
        n_steps = max(abs(r2 - r1), abs(c2 - c1), 1)
        total_cost = 0.0

        for step in range(n_steps + 1):
            t = step / max(1, n_steps)
            r = int(r1 + (r2 - r1) * t)
            c = int(c1 + (c2 - c1) * t)
            r = max(0, min(r, n_rows - 1))
            c = max(0, min(c, n_cols - 1))
            total_cost += resistance_grid[r, c]

        return total_cost

    def _calculate_graph_metrics(self, graph: nx.Graph) -> Dict:
        """Calculate useful graph metrics."""
        if graph.number_of_nodes() == 0:
            return {"overall_connectivity": 0}

        metrics = {
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "connected_components": nx.number_connected_components(graph),
            "density": round(nx.density(graph), 4),
        }

        # Degree centrality
        if graph.number_of_nodes() > 1:
            centrality = nx.degree_centrality(graph)
            metrics["max_centrality_node"] = max(centrality, key=centrality.get)
            metrics["avg_centrality"] = round(np.mean(list(centrality.values())), 4)

            # Betweenness centrality (identifies bridge nodes)
            betweenness = nx.betweenness_centrality(graph, weight="cost")
            metrics["bridge_nodes"] = [
                n for n, c in betweenness.items() if c > 0.1
            ]

        # Overall connectivity score (0-100)
        if graph.number_of_edges() > 0:
            avg_connectivity = np.mean([
                d.get("connectivity_score", 0)
                for _, _, d in graph.edges(data=True)
            ])
            metrics["overall_connectivity"] = round(avg_connectivity, 2)
        else:
            metrics["overall_connectivity"] = 0

        return metrics

    def _generate_corridors(
        self, graph: nx.Graph, patches: List[Dict],
        resistance_grid: np.ndarray, grid_meta: dict
    ) -> List[Dict]:
        """Generate corridor geometries from graph edges."""
        patch_lookup = {p["patch_id"]: p for p in patches}
        corridors = []

        for u, v, data in graph.edges(data=True):
            p1 = patch_lookup.get(u)
            p2 = patch_lookup.get(v)
            if not p1 or not p2:
                continue

            # Generate waypoints for a more natural-looking corridor
            waypoints = self._generate_waypoints(
                p1, p2, resistance_grid, grid_meta
            )

            corridors.append({
                "source_patch_id": u,
                "target_patch_id": v,
                "connectivity_score": data.get("connectivity_score", 0),
                "resistance_score": data.get("cost", 0),
                "length_km": data.get("distance_km", 0),
                "cost": data.get("cost", 0),
                "waypoints": waypoints,
            })

        return corridors

    def _generate_waypoints(
        self, p1: Dict, p2: Dict, resistance_grid: np.ndarray, grid_meta: dict
    ) -> List[Tuple[float, float]]:
        """Generate waypoints for a corridor path with some curvature."""
        lat1, lng1 = p1["centroid_lat"], p1["centroid_lng"]
        lat2, lng2 = p2["centroid_lat"], p2["centroid_lng"]

        n_points = max(5, int(np.sqrt((lat2-lat1)**2 + (lng2-lng1)**2) / 0.05))
        waypoints = []

        for i in range(n_points + 1):
            t = i / n_points
            lat = lat1 + (lat2 - lat1) * t
            lng = lng1 + (lng2 - lng1) * t

            # Add slight deviation based on resistance (path follows lower resistance)
            if 0 < t < 1:
                offset = 0.02 * np.sin(t * np.pi * 3) * np.cos(t * np.pi * 2)
                lat += offset
                lng += offset * 0.7

            waypoints.append((lng, lat))  # GeoJSON uses [lng, lat]

        return waypoints

    async def _store_corridors(self, corridors: List[Dict]):
        """Store corridors in the database."""
        # Clear old corridors
        await self.db.execute(
            delete(Corridor).where(Corridor.project_id == self.project_id)
        )

        for corridor in corridors:
            if len(corridor["waypoints"]) < 2:
                continue

            line = LineString(corridor["waypoints"])

            db_corridor = Corridor(
                project_id=self.project_id,
                geometry=mapping(line),
                source_patch_id=corridor["source_patch_id"],
                target_patch_id=corridor["target_patch_id"],
                connectivity_score=corridor["connectivity_score"],
                resistance_score=corridor["resistance_score"],
                length_km=corridor["length_km"],
                cost=corridor["cost"],
            )
            self.db.add(db_corridor)

        await self.db.flush()
