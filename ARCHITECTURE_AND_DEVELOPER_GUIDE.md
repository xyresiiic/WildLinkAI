# WildLink AI — Architecture & Developer Guide

Comprehensive technical documentation, architecture blueprint, mathematical algorithms, API reference, component hierarchy, and developer handbook for **WildLink AI**.

---

## Table of Contents
1. [Executive Overview & Problem Domain](#1-executive-overview--problem-domain)
2. [System Architecture Blueprint](#2-system-architecture-blueprint)
3. [Database Architecture & Data Models](#3-database-architecture--data-models)
4. [Computational Engines & Algorithms](#4-computational-engines--algorithms)
   - [Habitat Suitability Engine](#41-habitat-suitability-engine)
   - [Fragmentation Engine](#42-fragmentation-engine)
   - [Resistance Surface Engine](#43-resistance-surface-engine)
   - [Least-Cost Corridor & Graph Connectivity Engine](#44-least-cost-corridor--graph-connectivity-engine)
   - [Multi-Criteria Priority & Explainability Engine](#45-multi-criteria-priority--explainability-engine)
   - [What-If Simulation Engine](#46-what-if-simulation-engine)
5. [Backend API Reference](#5-backend-api-reference)
6. [Frontend Architecture & Component Hierarchy](#6-frontend-architecture--component-hierarchy)
7. [Testing & Verification Framework](#7-testing--verification-framework)
8. [Setup, Deployment & Launchers](#8-setup-deployment--launchers)
9. [Developer Extension Guide & Roadmap](#9-developer-extension-guide--roadmap)

---

## 1. Executive Overview & Problem Domain

### 1.1 Purpose & Mission
WildLink AI is an advanced agentic GIS platform designed to calculate, visualize, and simulate wildlife habitat corridors, landscape fragmentation, and spatial conservation priorities across India's key biogeographic zones. Each species is modeled within its authentic geographic range:
- **Western Himalayas**: Ladakh & Spiti Valley (Snow Leopard)
- **North Indian River Basins**: National Chambal River Sanctuary (Gharial)
- **Thar Desert**: Jaisalmer Semi-Arid Grasslands (Great Indian Bustard)
- **Western Ghats**: Nilgiri Biosphere Elephant Corridor (Indian Elephant)
- **Central Indian Highlands**: Kanha–Bandhavgarh–Pench Tiger Landscape (Bengal Tiger)
- **Satpura & Aravalli**: Rocky Hill & Scrub Ecotones (Indian Leopard)
- **Deccan Plateau**: Daroji Sloth Bear Sanctuary (Sloth Bear)

### 1.2 Target Species & Authentic Biogeographic Ranges
| Species | Scientific Name | Conservation Status | Authentic Native Region in India | Key Protected Reserves & Coordinates |
| :--- | :--- | :--- | :--- | :--- |
| **Bengal Tiger** | *Panthera tigris tigris* | Endangered | Central Indian Highlands | Kanha `(22.33, 80.62)`, Bandhavgarh `(23.70, 81.03)`, Pench `(21.75, 79.35)` |
| **Snow Leopard** | *Panthera uncia* | Vulnerable | Western Himalayas (Ladakh & Spiti) | Hemis NP `(33.95, 77.45)`, Kibber WLS `(32.33, 78.01)`, Pin Valley `(31.95, 77.85)` |
| **Gharial** | *Gavialis gangeticus* | Critically Endangered | National Chambal River Sanctuary | Chambal-Morena `(26.65, 77.90)`, Sheopur `(26.45, 77.35)`, Etawah Confluence `(26.78, 79.03)` |
| **Great Indian Bustard** | *Ardeotis nigriceps* | Critically Endangered | Thar Desert & Semi-Arid Grasslands | Desert NP `(26.85, 70.55)`, Sudasari `(26.75, 70.60)`, Ramdevra `(27.02, 71.95)` |
| **Indian Elephant** | *Elephas maximus indicus* | Endangered | Western Ghats & Nilgiri Biosphere | Bandipur `(11.66, 76.62)`, Nagarhole `(11.95, 76.25)`, Wayanad `(11.70, 76.35)`, Mudumalai `(11.58, 76.55)` |
| **Indian Leopard** | *Panthera pardus fusca* | Vulnerable | Satpura & Aravalli Rocky Landscape | Jawai Hills `(25.10, 73.15)`, Satpura Foothills `(22.55, 77.95)`, Kumbhalgarh `(25.15, 73.58)` |
| **Sloth Bear** | *Melursus ursinus* | Vulnerable | Daroji & Deccan Boulder Plateau | Daroji Sloth Bear Sanctuary `(15.25, 76.60)`, Gudekote `(14.88, 76.65)`, Bori `(22.48, 78.02)` |

---

## 2. System Architecture Blueprint

```
+-------------------------------------------------------------------------------+
|                             REACT 18 SPA (Vite)                               |
|  +--------------------+  +-------------------------+  +--------------------+  |
|  |     Header.jsx     |  | ConservationMap.jsx     |  |    Sidebar.jsx     |  |
|  | - Project Selector |  | - Leaflet GeoJSON Layers|  | - Layer Toggles    |  |
|  | - Species Badges   |  | - Suitability Heatmaps  |  | - Analysis Controls|  |
|  | - Export JSON CTA  |  | - Corridor LineStrings  |  | - Priority Zones   |  |
|  +--------------------+  | - Interactive Tooltips  |  | - Metrics Cards    |  |
|                          +-------------------------+  +--------------------+  |
|                                       |                                       |
|  +------------------------------------+------------------------------------+  |
|  |  SimulationPanel.jsx (What-If)     |   ZoneDetailModal.jsx (Inspector)  |  |
+---------------------------------------+---------------------------------------+
                                        | Axios HTTP (/api/v1)
                                        v
+-------------------------------------------------------------------------------+
|                             FASTAPI BACKEND                                   |
|  +-------------------------------------------------------------------------+  |
|  | API Routers: /species  /projects  /analysis  /simulations  /dashboard  |  |
|  +-------------------------------------------------------------------------+  |
|  | Background Tasks Worker (run_full_analysis / run_simulation)            |  |
|  +-------------------------------------------------------------------------+  |
|                                       |                                       |
|  +------------------------------------+------------------------------------+  |
|  |                     ANALYTICAL GIS ENGINE PIPELINE                      |  |
|  |                                                                         |  |
|  |  [1] HabitatEngine       --> Spatial Suitability Grid [0..1]           |  |
|  |  [2] FragmentationEngine --> Connected Patches (SciPy label) & Metrics |  |
|  |  [3] ResistanceEngine    --> Cost-Surface Matrix [1..100]              |  |
|  |  [4] ConnectivityEngine  --> Least-Cost Dijkstra Corridors & Graph     |  |
|  |  [5] PriorityEngine      --> Multi-Criteria Ranks & Explainability      |  |
|  |  [6] SimulationEngine    --> What-If Scenarios & Delta Gain Calculation|  |
|  +-------------------------------------------------------------------------+  |
|                                       |                                       |
|                                       v                                       |
|                      SQLAlchemy 2.0 (Async + Sync Engines)                    |
|                      SQLite (WAL Mode + busy_timeout=60s)                     |
+-------------------------------------------------------------------------------+
```

---

## 3. Database Architecture & Data Models

### 3.1 Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ PROJECTS : creates
    SPECIES ||--o{ OBSERVATIONS : has
    SPECIES ||--o{ PROJECTS : targets
    PROJECTS ||--o{ HABITAT_ZONES : contains
    PROJECTS ||--o{ CORRIDORS : contains
    PROJECTS ||--o{ PRIORITY_ZONES : contains
    PROJECTS ||--o{ SIMULATIONS : evaluates
    PROJECTS ||--o{ ANALYSIS_JOBS : tracks

    USERS {
        string id PK
        string name
        string email
        string password_hash
        string role
        datetime created_at
    }

    SPECIES {
        string id PK
        string common_name
        string scientific_name
        string description
        json habitat_preferences
        string conservation_status
        string image_url
    }

    PROJECTS {
        string id PK
        string name
        string description
        json region_geometry
        string region_name
        string species_id FK
        string created_by FK
        string status
        datetime created_at
    }

    OBSERVATIONS {
        string id PK
        string species_id FK
        float latitude
        float longitude
        datetime observed_at
        string source
        float confidence
        json metadata
    }

    HABITAT_ZONES {
        string id PK
        string project_id FK
        json geometry
        float suitability_score
        float area_hectares
        int patch_id
        float perimeter_km
        float compactness
        float nearest_patch_distance_km
        string fragmentation_level
        json metadata
    }

    CORRIDORS {
        string id PK
        string project_id FK
        json geometry
        int source_patch_id
        int target_patch_id
        float connectivity_score
        float resistance_score
        float length_km
        float cost
        json metadata
    }

    PRIORITY_ZONES {
        string id PK
        string project_id FK
        json geometry
        int rank
        float priority_score
        string priority_level
        float habitat_score
        float connectivity_score
        float species_score
        float restoration_score
        float constraint_score
        string dominant_factor
        string explanation
        string evidence_quality
        json factors_json
        float area_hectares
    }

    SIMULATIONS {
        string id PK
        string project_id FK
        string name
        string intervention_type
        json zone_ids
        json parameters
        float restoration_area_ha
        float baseline_connectivity
        float simulated_connectivity
        float improvement
        float percentage_change
        json result
        string status
    }

    ANALYSIS_JOBS {
        string id PK
        string project_id FK
        string type
        string status
        int progress
        json result
        string error
        datetime started_at
        datetime completed_at
    }
```

### 3.2 Backend Codebase & File Organization
| Module / Layer | File Location | Purpose & Responsibility |
| :--- | :--- | :--- |
| **ORM Data Models** | [models.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/models.py) | SQLAlchemy 2.0 ORM classes (`Species`, `Project`, `HabitatZone`, `Corridor`, `PriorityZone`, `Simulation`, etc.) |
| **Validation Schemas** | [schemas.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/schemas.py) | Pydantic v2 request/response validation contracts |
| **Database Sessions** | [database.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/database.py) | SQLite WAL mode, connection timeouts, and async engine pools |
| **Configuration** | [config.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/config.py) | Application settings and environment variables |
| **Security & Auth** | [security.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/security.py) | JWT authentication, hashing, and token verification |
| **GIS Helpers** | [utils.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/utils.py) | GeoJSON serialization and API response packaging |
| **Species Routes** | [species_routes.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/api/species_routes.py) | FastAPI endpoints for species discovery and ecological profiles |
| **Project Routes** | [project_routes.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/api/project_routes.py) | Project CRUD, dashboard metrics aggregations, and GeoJSON bundle export |
| **Analysis Routes** | [analysis_routes.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/api/analysis_routes.py) | Async GIS pipeline execution and layer retrieval |
| **Simulation Routes** | [simulation_routes.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/api/simulation_routes.py) | What-If simulation management and scenario comparisons |
| **Pipeline Service** | [analysis_service.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/services/analysis_service.py) | 5-stage background pipeline coordinator |
| **Simulation Service**| [simulation_service.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/services/simulation_service.py) | Counterfactual simulation scenario runner |

### 3.3 Database Engine Configuration
- **File**: `backend/app/database.py`
- **Driver**: `sqlite+aiosqlite` (Async) & `sqlite` (Sync fallback)
- **Concurrency & WAL Settings**:
  - `PRAGMA journal_mode=WAL;` (Write-Ahead Logging for non-blocking concurrent reads).
  - `PRAGMA busy_timeout=60000;` (Wait up to 60s during batch writes).
  - `connect_args={"timeout": 60}`.
  - `echo=False` to prevent stdout logging overhead during thousands of GIS inserts.

---

## 4. Computational Engines & Algorithms

All analytical engines reside in `backend/app/engines/` and extend the base async database pattern.

### 4.1 Habitat Suitability Engine
- **File**: [habitat_engine.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/engines/habitat_engine.py)
- **Grid Resolution**: Configurable via `DEFAULT_GRID_RESOLUTION` (default `0.045°` ≈ 5km).
- **Features Evaluated**:
  1. **Observation Proximity & Density**: Gaussian kernel distance decay from verified presence points:
     $$S_{\text{obs}}(x, y) = \sum_{i=1}^N w_i \exp\left(-\frac{d((x,y), p_i)^2}{2\sigma^2}\right)$$
  2. **Land Cover Suitability**: Synthetic landcover classification based on elevation, moisture, and vegetation indices tailored to species preferences.
  3. **Water Body Proximity**: Distance decay to major river systems (Narmada, Ken, Betwa, Son). Aquatic species (Gharial) receive exponential suitability boosts.
  4. **Elevation & Terrain Ruggedness**: Gaussian altitude distribution centered on species optimal elevation range.
  5. **Protected Area Coverage**: Buffer overlap with National Parks (Kanha, Bandhavgarh, Pench, Panna).
  6. **Human Disturbance & Road Density**: Inverse linear penalty based on proximity to National Highways (NH-44, NH-7).

### 4.2 Fragmentation Engine
- **File**: [fragmentation_engine.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/engines/fragmentation_engine.py)
- **Connected Component Analysis**:
  - Binarizes suitability matrix with threshold $\tau = 0.50$.
  - Uses `scipy.ndimage.label(binary_grid, structure=np.ones((3,3)))` with 8-connectivity.
- **Morphological Spatial Metrics**:
  - **Core Area**: Total hectares per labeled component.
  - **Compactness Index**: Ratio of patch area to its convex bounding envelope.
  - **Nearest-Neighbor Distance**: Euclidean distance between patch centroids.
  - **Fragmentation Level**: Classified into `low`, `medium`, `high`.
- **High-Performance Bulk Updates**:
  - Utilizes SQLAlchemy 2.0 ORM bulk updates `await db.execute(update(HabitatZone), update_data)` executing single C-level `executemany` operations for thousands of zones in <100ms.

### 4.3 Resistance Surface Engine
- **File**: [resistance_engine.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/engines/resistance_engine.py)
- **Resistance Function**:
  $$R(x, y) = R_{\text{base}} + R_{\text{roads}} + R_{\text{settlements}} + R_{\text{water}} - B_{\text{PA}}$$
  Clamped to range $[1.0, 100.0]$.
  - $R_{\text{base}} = 100 \cdot (1.0 - S(x, y))$
  - $R_{\text{roads}} = 30 \cdot \exp(-d_{\text{NH}} / 0.3)$
  - $B_{\text{PA}} = 20.0$ if inside protected reserve boundaries.

### 4.4 Least-Cost Corridor & Graph Connectivity Engine
- **File**: [connectivity_engine.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/engines/connectivity_engine.py)
- **Least-Cost Path (LCP)**:
  - Dijkstra shortest path on 8-neighbor weighted grid with cell transition costs:
    $$\text{Cost}(u \to v) = \frac{R(u) + R(v)}{2} \cdot \text{dist}(u, v)$$
  - **Adaptive Search Padding**: Dynamically scales search bounding box buffer based on inter-patch distance:
    $$\text{pad} = \max\left(15, \lfloor\max(|r_2 - r_1|, |c_2 - c_1|) \cdot 0.35\rfloor\right)$$
- **Graph Topology**:
  - Constructed using `networkx.Graph()`.
  - Computes global algebraic connectivity, edge density, and component subgraphs.
  - Generates GeoJSON `LineString` corridors stored in the `corridors` table.

### 4.5 Multi-Criteria Priority & Explainability Engine
- **File**: [priority_engine.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/engines/priority_engine.py)
- **Multi-Criteria Decision Analysis (MCDA)**:
  $$\text{Priority Score} = w_H S_H + w_C S_C + w_S S_S + w_R S_R - w_K S_K$$
  - $S_H$: Habitat Suitability Score
  - $S_C$: Connectivity Criticality Score (Betweenness centrality)
  - $S_S$: Species Vulnerability / Conservation Weight
  - $S_R$: Restoration Opportunity Potential
  - $S_K$: Development / Linear Infrastructure Threat Constraint
- **AI Explainability**:
  - Dynamically extracts the `dominant_factor` (`Corridor Stepping Stone`, `Core Breeding Sanctuary`, `High Degradation Risk`, etc.).
  - Generates structured natural language justifications and actionable policy recommendations.

### 4.6 What-If Simulation Engine
- **File**: [simulation_engine.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/backend/app/engines/simulation_engine.py)
- **Intervention Types**:
  1. `habitat_restoration`: Reduces local resistance by up to 60% across selected zones.
  2. `barrier_removal`: Models eco-ducts and underpasses across road intersections.
  3. `corridor_protection`: Upgrades legal protection status, eliminating human encroachment resistance.
- **Delta Evaluation**: Re-runs resistance surface and graph metrics to output baseline connectivity, simulated connectivity, absolute improvement, and percentage change.

---

## 5. Backend API Reference

Base Prefix: `/api/v1`

### 5.1 Species Endpoints
- `GET /species` — List all registered species with conservation status, habitat preferences, and profile images.
- `GET /species/{species_id}` — Get single species details.
- `POST /species` — Register new species profile.

### 5.2 Project Endpoints
- `GET /projects` — List all conservation projects.
- `GET /projects/{project_id}` — Get project metadata, target species, and bounding region.
- `POST /projects` — Create a new project.
- `DELETE /projects/{project_id}` — Delete project and cascade-delete all associated zones, corridors, and simulations.
- `GET /projects/{project_id}/dashboard` (or `GET /dashboard/{project_id}`) — Aggregate summary statistics, patch counts, corridor counts, and average scores.
- `GET /projects/{project_id}/export` — Complete export bundle including project metadata, executive summary, and GeoJSON `FeatureCollection` layers.

### 5.3 Analysis Endpoints
- `POST /analysis/run` — Trigger asynchronous background analysis job (`habitat`, `fragmentation`, `connectivity`, `priority`, or `full`).
- `GET /analysis/jobs/{job_id}` — Poll job status, progress percentage (`0..100`), and error reports.
- `GET /analysis/habitat/{project_id}` — GeoJSON `Polygon` features of all habitat zones with suitability scores.
- `GET /analysis/corridors/{project_id}` — GeoJSON `LineString` features of least-cost corridors with connectivity metrics.
- `GET /analysis/priority/{project_id}` — GeoJSON `Polygon` features of top-ranked priority zones with natural language explanations.
- `GET /analysis/observations/{project_id}` — GeoJSON `Point` features of species observation coordinates.

### 5.4 Simulation Endpoints
- `POST /simulations` (or `POST /simulations/run`) — Queue a What-If counterfactual scenario.
- `GET /simulations/{simulation_id}` — Get scenario status and delta connectivity results.
- `GET /simulations/project/{project_id}` — List all simulations created for a project.

---

## 6. Frontend Architecture & Component Hierarchy

Built with React 18, Vite, and Leaflet with a dark glassmorphic design system in [index.css](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/frontend/src/index.css).

```
frontend/src/
├── main.jsx                   # React root entry point
├── App.jsx                    # Root state coordinator, project switcher, toast system
├── index.css                  # Design tokens, neon accents, dark mode glassmorphism
├── services/
│   └── api.js                 # Axios API client with Vite proxy & environment config
└── components/
    ├── Header.jsx             # Top navbar, project selector, species status chip, export CTA
    ├── Sidebar.jsx            # Multi-tab drawer:
    │                          #   - Layer Visibility Toggles
    │                          #   - Analysis Weight Sliders & Trigger
    │                          #   - Ranked Priority Zone Cards
    │                          #   - Key Metrics Dashboard Cards
    ├── Map/
    │   └── ConservationMap.jsx # Interactive Leaflet map:
    │                          #   - Observations (Pulsing CircleMarkers)
    │                          #   - Habitat Zones (Suitability-colored Polygons)
    │                          #   - Corridors (Glowing PolyLines with pulse animations)
    │                          #   - Priority Zones (Numbered Rank Badges & Highlights)
    ├── SimulationPanel.jsx    # What-If scenario builder, pre-selection, before/after charts
    └── ZoneDetailModal.jsx    # Deep-dive zone inspector with radar scores & AI rationale
```

---

## 7. Testing & Verification Framework

### 7.1 System Integration Test Suite
- **File**: [scripts/test_full_suite.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/scripts/test_full_suite.py)
- **Scope**: Tests all 11 core functional areas against the FastAPI ASGI test client:
  1. Health check `/health` and `/api/v1/health`
  2. Species listing `/species`
  3. Project creation `/projects`
  4. Species observations retrieval `/analysis/observations/{id}`
  5. Full pipeline background execution `/analysis/run`
  6. Habitat zone polygon validation
  7. Corridor LineString least-cost path validation
  8. Priority zone ranking and explainability
  9. What-If counterfactual simulation
  10. Dashboard statistical aggregations `/projects/{id}/dashboard`
  11. Conservation GeoJSON export bundle `/projects/{id}/export`

### 7.2 Multi-Species Verification Suite
- **File**: [scripts/verify_all_categories.py](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/scripts/verify_all_categories.py)
- **Scope**: Executes the complete 5-engine pipeline across all 7 species categories, generating a comparative metrics table.

---

## 8. Setup, Deployment & Launchers

### 8.1 Prerequisites
- **Python**: 3.10+ (Virtual environment recommended)
- **Node.js**: 18+ & npm

### 8.2 One-Click Startup Scripts
- **Windows Batch**: Double-click [start_app.bat](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/start_app.bat)
- **Windows PowerShell**: Run `.\start_app.ps1`
- **Linux / macOS**: Run `./start_app.sh`

### 8.3 Manual Startup
```bash
# 1. Start Backend
cd backend
venv\Scripts\activate   # Linux/macOS: source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 2. Start Frontend
cd ../frontend
npm install
npm run dev
```

- Web Application: `http://localhost:5173`
- API Documentation: `http://127.0.0.1:8000/docs`

### 8.3 Vercel Deployment Configuration
WildLink AI includes root and frontend Vercel deployment manifests:
- [vercel.json](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/vercel.json): Root configuration coordinating `@vercel/static-build` (React/Vite in `frontend/`) and `@vercel/python` (FastAPI in `api/index.py`).
- [frontend/vercel.json](file:///d:/Projects/Hackathon%20Projects/WildLife%20AI/frontend/vercel.json): Single-page app (SPA) fallback rewrite rules when deploying directly from the `frontend/` directory.

---

## 9. Developer Extension Guide & Roadmap

### 9.1 How to Add a New Species
1. Open `backend/app/main.py` in `_seed_demo_data()`.
2. Add a new `Species` instance with name, scientific name, conservation status, and `habitat_preferences`:
   ```python
   Species(
       common_name="Barasingha",
       scientific_name="Rucervus duvaucelii branderi",
       description="Hardground swamp deer endemic to Kanha National Park meadows.",
       conservation_status="Vulnerable",
       habitat_preferences={
           "preferred_elevation_min": 300,
           "preferred_elevation_max": 700,
           "water_affinity": 0.9,
           "forest_canopy_preference": 0.4,
           "grassland_preference": 0.95,
           "human_tolerance": 0.1,
       },
       image_url="https://images.unsplash.com/photo-example"
   )
   ```
3. Add sample presence observation coordinates to `_generate_observations_for_species()`.
4. Run the seed or re-initialize the database.

### 9.2 How to Add a New Analytical GIS Engine
1. Create `backend/app/engines/new_engine.py` inheriting standard database session access:
   ```python
   class ClimateResilienceEngine:
       def __init__(self, project_id: str, db: AsyncSession):
           self.project_id = project_id
           self.db = db
       async def run(self):
           # Calculations
           return {"resilience_score": 85.0}
   ```
2. Integrate into `backend/app/services/analysis_service.py` within `run_full_analysis()`.
3. Add any new database fields in `backend/app/models/models.py` and Pydantic response schemas in `schemas.py`.

### 9.3 Production Migration to PostgreSQL + PostGIS
1. In `backend/app/core/config.py`, change `DATABASE_URL` to:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/wildlink
   ```
2. Replace `JSON` geometry columns with native `geoalchemy2.Geometry("POLYGON", srid=4326)`.
3. Leverage spatial indexes (`GIST`) for accelerated bounding box queries.

---

## 10. Vercel Serverless Architecture & Optimization

### 10.1 Serverless Environment Constraints & Adaptations
| Constraint | Challenge | Solution Implemented |
| :--- | :--- | :--- |
| **Read-Only Filesystem** | `/var/task` deployment root is read-only | SQLite database dynamically copied and routed to `/tmp/wildlink.db` with automatic fallback discovery. |
| **Strict 10s Timeout** | Heavy spatial loops cause 504 Gateway Timeouts | Replaced pairwise polygon geometric distance loops with `scipy.spatial.cKDTree` spatial indexing (< 20ms) and adaptive grid resolution (`0.08°`). |
| **Post-Response Freeze** | Serverless runtimes freeze background threads once HTTP response is emitted | In serverless environments (`VERCEL` / `AWS_LAMBDA_FUNCTION_NAME`), analysis runs synchronously in **1.2s - 3.8s** before HTTP response completion. |
| **Bundle Size < 500MB** | Heavy C/GDAL binaries (`rasterio`, `fiona`, `geopandas`) exceeded 623MB | Trimmed dependencies to pure Python GIS equivalents (`shapely`, `networkx`, `scipy`, `scikit-learn`), reducing package bundle to ~110MB. |
| **Instant Cold Boot** | Heavy computation during app initialization causes timeouts | Pre-seeded database bundled in `backend/wildlink.db` with non-blocking cold-start startup routines. |
| **Stateless Polling Glitches** | Polling job IDs across ephemeral serverless instances returned 404s | `trigger_analysis` returns `status="completed"` synchronously; `get_job_status` and frontend `pollJobStatus` implement auto-recovery fallback to project layer metrics. |

### 10.2 Serverless Job Status Resiliency & Auto-Recovery Flow
1. **Synchronous Analysis Dispatch**:
   - `POST /api/v1/analysis/run` finishes execution in ~2s on Vercel and returns `status="completed"`, `progress=100`, eliminating the requirement for post-run polling across ephemeral lambdas.
2. **Multi-Instance Auto-Recovery**:
   - `GET /api/v1/analysis/jobs/{job_id}` returns a completed status envelope if queried on a stateless instance.
   - Frontend `handleRunAnalysis` checks `getDashboard(projectId)` to instantly recover and display active GIS models if a network glitch occurs.

### 10.3 Deterministic UUID5 Strategy for Cross-Deployment Stability
- **Problem**: Vercel redeployments create fresh serverless instances. If the bundled `wildlink.db` is re-seeded, random `uuid4()` IDs for species and projects change. Users with stale project IDs bookmarked or cached in `window.location.hash` receive 404 errors.
- **Solution**: `_deterministic_id(namespace_label)` in `backend/app/main.py` uses `uuid.uuid5(WILDLINK_NS, label)` with a fixed namespace UUID. Species IDs are derived from `species:{scientific_name}` and project IDs from `project:{scientific_name}`, ensuring identical UUIDs across all cold starts and redeployments.
- **Frontend Resilience**: `checkUrlHash()` in `App.jsx` auto-recovers from stale project hashes by reloading the projects list and selecting the first available project. `handleRunAnalysis` detects 404 responses from stale project IDs and transparently re-resolves the correct project for the selected species before retrying.
