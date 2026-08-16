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

        for pid, group in patch_groups.items():
            if len(group["zones"]) < 3:
                continue  # Skip very small patches in primary pass

            lats, lngs = [], []
            for zone in group["zones"]:
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
                "centroid_lat": float(np.mean(lats)),
                "centroid_lng": float(np.mean(lngs)),
                "area_hectares": float(sum(z.area_hectares or 0 for z in group["zones"])),
                "avg_suitability": float(np.mean(group["suitability_scores"])),
                "zone_count": len(group["zones"]),
            })

        # Fallback if fewer than 2 patches meet the >=3 zone threshold
        if len(patches) < 2:
            existing_pids = {p["patch_id"] for p in patches}
            for pid, group in patch_groups.items():
                if pid in existing_pids:
                    continue
                lats, lngs = [], []
                for zone in group["zones"]:
                    try:
                        geom_shape = shape(zone.geometry) if isinstance(zone.geometry, dict) else None
                        if geom_shape:
                            centroid = geom_shape.centroid
                            lats.append(centroid.y)
                            lngs.append(centroid.x)
                    except Exception:
                        pass
                if lats:
                    patches.append({
                        "patch_id": pid,
                        "centroid_lat": float(np.mean(lats)),
                        "centroid_lng": float(np.mean(lngs)),
                        "area_hectares": float(sum(z.area_hectares or 0 for z in group["zones"])),
                        "avg_suitability": float(np.mean(group["suitability_scores"])),
                        "zone_count": len(group["zones"]),
                    })

        # Keep top significant habitat patches for robust & fast corridor generation
        patches.sort(key=lambda p: p["area_hectares"], reverse=True)
        return patches[:25]

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
        """Compute least-cost path cost between two patch centroids using Dijkstra on resistance surface."""
        path, cost = self._find_least_cost_path(p1, p2, resistance_grid, grid_meta)
        return cost

    def _generate_waypoints(
        self, p1: Dict, p2: Dict, resistance_grid: np.ndarray, grid_meta: dict
    ) -> List[Tuple[float, float]]:
        """Generate least-cost path waypoints on the resistance surface."""
        path, _ = self._find_least_cost_path(p1, p2, resistance_grid, grid_meta)
        if len(path) < 2:
            return [(p1["centroid_lng"], p1["centroid_lat"]), (p2["centroid_lng"], p2["centroid_lat"])]

        waypoints = []
        resolution = grid_meta["resolution"]
        min_lat = grid_meta["min_lat"]
        min_lng = grid_meta["min_lng"]

        # Sample path points to keep GeoJSON clean and smooth
        step = max(1, len(path) // 30)
        sampled_path = path[::step]
        if path[-1] not in sampled_path:
            sampled_path.append(path[-1])

        for r, c in sampled_path:
            lat = min_lat + r * resolution + resolution / 2
            lng = min_lng + c * resolution + resolution / 2
            waypoints.append((round(float(lng), 5), round(float(lat), 5)))

        return waypoints

    def _find_least_cost_path(
        self, p1: Dict, p2: Dict, resistance_grid: np.ndarray, grid_meta: dict
    ) -> Tuple[List[Tuple[int, int]], float]:
        """Find the optimal least-cost path between two centroids using 8-connected Dijkstra search."""
        import heapq
        resolution = grid_meta["resolution"]
        n_rows = grid_meta["n_rows"]
        n_cols = grid_meta["n_cols"]

        r1 = max(0, min(int((p1["centroid_lat"] - grid_meta["min_lat"]) / resolution), n_rows - 1))
        c1 = max(0, min(int((p1["centroid_lng"] - grid_meta["min_lng"]) / resolution), n_cols - 1))
        r2 = max(0, min(int((p2["centroid_lat"] - grid_meta["min_lat"]) / resolution), n_rows - 1))
        c2 = max(0, min(int((p2["centroid_lng"] - grid_meta["min_lng"]) / resolution), n_cols - 1))

        if r1 == r2 and c1 == c2:
            return [(r1, c1)], float(resistance_grid[r1, c1])

        # Bounding box with adaptive buffer around endpoints to optimize search speed & route quality
        pad = max(15, int(max(abs(r2 - r1), abs(c2 - c1)) * 0.35))
        min_r, max_r = max(0, min(r1, r2) - pad), min(n_rows - 1, max(r1, r2) + pad)
        min_c, max_c = max(0, min(c1, c2) - pad), min(n_cols - 1, max(c1, c2) + pad)

        pq = [(0.0, r1, c1)]
        dist = {(r1, c1): 0.0}
        parent = {}

        directions = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)
        ]

        found = False
        while pq:
            d, r, c = heapq.heappop(pq)
            if (r, c) == (r2, c2):
                found = True
                break
            if d > dist.get((r, c), float("inf")):
                continue

            for dr, dc, step_cost in directions:
                nr, nc = r + dr, c + dc
                if min_r <= nr <= max_r and min_c <= nc <= max_c:
                    res_val = (resistance_grid[r, c] + resistance_grid[nr, nc]) / 2.0
                    edge_cost = res_val * step_cost
                    new_dist = d + edge_cost

                    if new_dist < dist.get((nr, nc), float("inf")):
                        dist[(nr, nc)] = new_dist
                        parent[(nr, nc)] = (r, c)
                        heapq.heappush(pq, (new_dist, nr, nc))

        # Reconstruct path
        if not found:
            # Fallback to straight-line interpolation
            n_steps = max(abs(r2 - r1), abs(c2 - c1), 1)
            line_path = []
            cost = 0.0
            for i in range(n_steps + 1):
                t = i / max(1, n_steps)
                lr = int(r1 + (r2 - r1) * t)
                lc = int(c1 + (c2 - c1) * t)
                line_path.append((lr, lc))
                cost += float(resistance_grid[lr, lc])
            return line_path, cost

        curr = (r2, c2)
        path = [curr]
        while curr in parent:
            curr = parent[curr]
            path.append(curr)
        path.reverse()

        return path, float(dist.get((r2, c2), 0.0))

    def _calculate_graph_metrics(self, G: nx.Graph) -> dict:
        """Calculate network graph metrics."""
        if G.number_of_nodes() == 0:
            return {"overall_connectivity": 0.0, "density": 0.0, "connected_components": 0}

        try:
            density = float(nx.density(G))
        except Exception:
            density = 0.0

        try:
            num_components = nx.number_connected_components(G)
        except Exception:
            num_components = 1

        edge_scores = [d.get("connectivity_score", 50.0) for _, _, d in G.edges(data=True)]
        avg_score = float(np.mean(edge_scores)) if edge_scores else 50.0

        return {
            "overall_connectivity": round(avg_score, 2),
            "density": round(density, 4),
            "connected_components": num_components,
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
        }

    def _generate_corridors(
        self, graph: nx.Graph, patches: List[Dict], resistance_grid: np.ndarray, grid_meta: dict
    ) -> List[Dict]:
        """Generate corridor objects from graph edges."""
        patch_lookup = {p["patch_id"]: p for p in patches}
        corridors = []

        for u, v, data in graph.edges(data=True):
            p1 = patch_lookup.get(u)
            p2 = patch_lookup.get(v)
            if not p1 or not p2:
                continue

            waypoints = self._generate_waypoints(p1, p2, resistance_grid, grid_meta)
            corridors.append({
                "source_patch_id": u,
                "target_patch_id": v,
                "connectivity_score": data.get("connectivity_score", 50.0),
                "resistance_score": data.get("cost", 50.0),
                "length_km": data.get("distance_km", 10.0),
                "cost": data.get("cost", 50.0),
                "waypoints": waypoints,
            })

        return corridors

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
