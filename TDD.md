# WILDLINK AI

## Technical Design Document (TDD)

### AI-Powered Wildlife Habitat Connectivity & Conservation Prioritization Platform

**Document Version:** 1.0
**Document Status:** Technical Baseline
**Product:** WildLink AI
**Domain:** Wildlife Protection & Conservation
**Architecture:** AI + GIS + Web Platform
**Target:** Hackathon MVP + Future Production Architecture
**Team Size:** 3 Developers
**Primary Development Model:** Modular Monolith + Background Processing

---

# 1. DOCUMENT PURPOSE

This Technical Design Document defines the technical architecture, software components, data architecture, algorithms, APIs, infrastructure, security model, development structure, testing strategy, deployment strategy, and implementation plan for **WildLink AI**.

The document converts the WildLink Product Requirements Document into an implementation-ready engineering specification.

The goal is not merely to describe what WildLink does, but to define:

> **How WildLink will actually be built.**

---

# 2. PRODUCT TECHNICAL DEFINITION

WildLink AI is a web-based conservation intelligence platform that combines:

* geospatial analysis
* ecological datasets
* machine learning
* graph-based connectivity analysis
* spatial databases
* optimization
* interactive visualization

to help conservation planners identify potentially high-value habitat connectivity and restoration zones.

The technical pipeline is:

```text
DATA
  ↓
INGESTION
  ↓
VALIDATION
  ↓
SPATIAL PROCESSING
  ↓
HABITAT SUITABILITY
  ↓
FRAGMENTATION
  ↓
RESISTANCE MODEL
  ↓
CONNECTIVITY
  ↓
PRIORITY SCORING
  ↓
WHAT-IF SIMULATION
  ↓
DECISION SUPPORT
```

---

# 3. TECHNICAL OBJECTIVES

The architecture must satisfy six major objectives.

## 3.1 Analytical

Support ecological and spatial analysis.

## 3.2 Interactive

Allow users to explore results visually through maps.

## 3.3 Explainable

Every important recommendation should have a traceable reason.

## 3.4 Scalable

The architecture should support additional species, datasets and geographic regions.

## 3.5 Reliable

Invalid or incomplete data should not silently produce misleading outputs.

## 3.6 Hackathon-Feasible

The architecture must be achievable by a three-person team within the available development period.

---

# 4. DESIGN PRINCIPLES

## Principle 1 — Decision First

The system exists to support a conservation decision, not simply display data.

## Principle 2 — Evidence Before AI

AI should operate on validated data.

## Principle 3 — Explainability

A model output without an explanation is insufficient for the primary use case.

## Principle 4 — Human in the Loop

WildLink recommends; conservation professionals decide.

## Principle 5 — Spatial by Design

Geospatial processing is a core capability, not an optional feature.

## Principle 6 — Modular Architecture

Each major analytical component should be independently replaceable.

## Principle 7 — MVP Discipline

The first implementation should focus on:

**one species + one landscape + one decision problem.**

---

# 5. HIGH-LEVEL SYSTEM ARCHITECTURE

```text
                         ┌──────────────────────┐
                         │        USER          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   React Web Client   │
                         └──────────┬───────────┘
                                    │ HTTPS / REST
                                    ▼
                     ┌─────────────────────────────┐
                     │       FastAPI Backend       │
                     │                             │
                     │ Auth                       │
                     │ Projects                   │
                     │ Species                    │
                     │ Analysis                   │
                     │ Priority                   │
                     │ Simulation                 │
                     └──────────────┬──────────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
        ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
        │   GIS Engine   │ │   ML Engine    │ │ Simulation     │
        │                │ │                │ │ Engine         │
        └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
                │                  │                  │
                └──────────────────┼──────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │ PostgreSQL + PostGIS │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Data / Raster Store  │
                         └──────────────────────┘
```

---

# 6. ARCHITECTURAL DECISION

## Chosen Architecture

### Modular Monolith

WildLink will initially use a modular monolithic backend rather than microservices.

### Why?

The team consists of only three developers.

Microservices would introduce unnecessary complexity:

* service discovery
* multiple deployments
* network communication
* distributed logging
* service authentication
* additional DevOps overhead

The modular monolith provides:

* faster development
* simpler deployment
* easier debugging
* shared Python environment
* direct access to GIS/ML modules

The architecture can later be decomposed into services if scale requires it.

---

# 7. MAJOR SYSTEM COMPONENTS

WildLink consists of:

1. Frontend Application
2. API Gateway/Application Backend
3. Authentication Module
4. Project Management Module
5. Data Ingestion Module
6. GIS Processing Engine
7. Habitat Suitability Engine
8. Fragmentation Engine
9. Connectivity Engine
10. Priority Engine
11. Simulation Engine
12. Reporting Engine
13. Database Layer
14. Background Job Processor
15. Monitoring and Logging

---

# 8. FRONTEND ARCHITECTURE

## Technology

* React
* JavaScript
* HTML
* CSS
* Leaflet or MapLibre
* Charting library
* REST API client

---

# 9. FRONTEND STRUCTURE

```text
frontend/
│
├── src/
│   ├── components/
│   │   ├── Map/
│   │   ├── Dashboard/
│   │   ├── Charts/
│   │   ├── Cards/
│   │   ├── Modals/
│   │   └── Common/
│   │
│   ├── pages/
│   │   ├── Login/
│   │   ├── Dashboard/
│   │   ├── Project/
│   │   ├── Analysis/
│   │   ├── Simulation/
│   │   └── Report/
│   │
│   ├── services/
│   │   ├── api.js
│   │   ├── projectService.js
│   │   ├── analysisService.js
│   │   └── simulationService.js
│   │
│   ├── hooks/
│   ├── context/
│   ├── utils/
│   ├── assets/
│   ├── App.jsx
│   └── main.jsx
│
└── package.json
```

---

# 10. FRONTEND APPLICATION FLOW

```text
Login
  ↓
Dashboard
  ↓
Select/Create Project
  ↓
Select Species
  ↓
Select Region
  ↓
Analysis Workspace
  ↓
Map + Analytical Layers
  ↓
Priority Zones
  ↓
What-If Simulator
  ↓
Scenario Comparison
  ↓
Report
```

---

# 11. MAP ARCHITECTURE

The map is the primary visualization interface.

It should support multiple layers.

## Base Layer

* Open geographic map

## Data Layers

* species observations
* protected areas
* roads
* settlements
* water bodies

## Analytical Layers

* habitat suitability
* fragmentation
* resistance
* potential corridors
* priority zones

---

# 12. MAP LAYER MODEL

Each layer should have:

```json
{
  "id": "habitat_suitability",
  "name": "Habitat Suitability",
  "type": "raster",
  "visible": true,
  "opacity": 0.7
}
```

The frontend should not contain ecological logic.

The backend should provide the analytical result.

---

# 13. BACKEND ARCHITECTURE

## Technology

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* PostGIS

Potential background processing:

* Celery/RQ or a lightweight worker implementation

For the hackathon, a simple background worker is preferable unless analysis workloads require a full task queue.

---

# 14. BACKEND STRUCTURE

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── species.py
│   │   ├── datasets.py
│   │   ├── analysis.py
│   │   ├── priority.py
│   │   ├── simulations.py
│   │   └── reports.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── species.py
│   │   ├── observation.py
│   │   ├── habitat.py
│   │   ├── corridor.py
│   │   └── simulation.py
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │   ├── project_service.py
│   │   ├── analysis_service.py
│   │   ├── priority_service.py
│   │   └── simulation_service.py
│   │
│   ├── engines/
│   │   ├── habitat_engine.py
│   │   ├── fragmentation_engine.py
│   │   ├── connectivity_engine.py
│   │   ├── priority_engine.py
│   │   └── simulation_engine.py
│   │
│   ├── database/
│   ├── core/
│   └── utils/
│
├── tests/
├── migrations/
└── requirements.txt
```

---

# 15. DATABASE ARCHITECTURE

## Selected Database

### PostgreSQL + PostGIS

PostGIS is necessary because WildLink must perform spatial operations such as:

* point-in-polygon
* intersection
* distance
* buffering
* spatial joins
* geometry filtering

---

# 16. DATABASE ENTITY MODEL

```text
                         USER
                          │
                          │ creates
                          ▼
                       PROJECT
                          │
              ┌───────────┼────────────┐
              │           │            │
              ▼           ▼            ▼
           SPECIES     DATASETS     ANALYSES
              │                        │
              ▼                        ▼
        OBSERVATIONS              RESULTS
                                       │
                  ┌────────────────────┼───────────────┐
                  ▼                    ▼               ▼
               HABITAT              CORRIDOR       PRIORITY
                                                        │
                                                        ▼
                                                   SIMULATION
```

---

# 17. CORE TABLES

## users

```text
id
name
email
password_hash
role
created_at
updated_at
```

## projects

```text
id
name
description
region_geometry
species_id
created_by
status
created_at
```

## species

```text
id
common_name
scientific_name
description
```

## observations

```text
id
species_id
location
observed_at
source
confidence
metadata
```

## datasets

```text
id
name
source
type
version
crs
quality
metadata
```

## habitat_zones

```text
id
project_id
geometry
suitability_score
area_hectares
```

## corridors

```text
id
project_id
geometry
connectivity_score
resistance_score
length_km
```

## priority_zones

```text
id
project_id
geometry
priority_score
habitat_score
connectivity_score
species_score
restoration_score
evidence_quality
explanation
```

## simulations

```text
id
project_id
name
parameters
baseline_score
simulated_score
improvement
result
created_at
```

---

# 18. SPATIAL INDEXING

Spatial tables must use spatial indexes.

Example:

```sql
CREATE INDEX idx_observations_location
ON observations
USING GIST(location);
```

Equivalent indexes should be created for:

* habitat geometry
* corridor geometry
* project boundaries
* priority zones
* infrastructure layers

This is essential when geographic datasets grow.

---

# 19. COORDINATE SYSTEM STRATEGY

The API may expose geographic coordinates using:

**WGS84 / EPSG:4326**

However, distance and area calculations should use an appropriate projected coordinate reference system.

The system should never assume that:

```text
1 degree = fixed physical distance
```

because geographic distance varies with latitude.

---

# 20. DATA INGESTION ENGINE

The ingestion engine is responsible for converting external datasets into WildLink-compatible structures.

Pipeline:

```text
Raw Dataset
    ↓
Format Detection
    ↓
Schema Validation
    ↓
Geometry Validation
    ↓
Coordinate Validation
    ↓
Duplicate Detection
    ↓
CRS Normalization
    ↓
Data Cleaning
    ↓
Database Import
```

---

# 21. SUPPORTED INPUT TYPES

Initial implementation:

* CSV
* GeoJSON
* GeoTIFF/raster where required

Future:

* Shapefile
* APIs
* remote sensing feeds
* additional biodiversity databases

---

# 22. DATA VALIDATION

The ingestion engine should check:

### Geometry

* valid coordinates
* valid polygons
* valid geometries

### Attributes

* required columns
* valid species identifiers
* numeric fields

### Quality

* missing values
* duplicates
* suspicious coordinates

Invalid records should be flagged instead of silently discarded.

---

# 23. SPECIES OBSERVATION PIPELINE

```text
Observation Dataset
       ↓
Extract Species
       ↓
Validate Coordinates
       ↓
Normalize CRS
       ↓
Remove Duplicates
       ↓
Store Point Geometry
       ↓
Spatial Index
       ↓
Analysis
```

---

# 24. HABITAT SUITABILITY ENGINE

The habitat engine estimates how suitable different spatial cells are for the selected species.

Conceptual architecture:

```text
Species Observations
        │
        ├── Land Cover
        ├── Vegetation
        ├── Water Distance
        ├── Elevation
        ├── Human Disturbance
        └── Protected Area
                │
                ▼
        Feature Engineering
                │
                ▼
             ML Model
                │
                ▼
       Suitability Probability
                │
                ▼
       Habitat Suitability Map
```

---

# 25. MACHINE LEARNING MODEL

## Recommended MVP Model

### Random Forest

Reasons:

* handles nonlinear relationships
* relatively robust
* interpretable
* supports feature importance
* fast enough for a prototype

The team should not choose a complex deep-learning architecture simply to make the project appear more "AI-based."

The model should be selected based on the available data.

---

# 26. HABITAT FEATURES

Potential features:

```text
land_cover_type
vegetation_index
elevation
distance_to_water
distance_to_observation
road_density
settlement_density
protected_area
human_disturbance
```

Only features supported by the selected dataset should be included.

---

# 27. HABITAT OUTPUT

Each spatial cell receives:

```text
Suitability ∈ [0,1]
```

For visualization:

```text
0.00–0.20 → Very Low
0.21–0.40 → Low
0.41–0.60 → Moderate
0.61–0.80 → High
0.81–1.00 → Very High
```

These categories are presentation defaults and should remain configurable.

---

# 28. MODEL VALIDATION

The system should evaluate:

* accuracy where appropriate
* precision
* recall
* F1
* ROC-AUC where meaningful
* feature importance

However, ecological presence-only data may require specialized validation approaches.

Therefore the project should not claim model accuracy without validating the specific dataset and methodology.

---

# 29. FRAGMENTATION ENGINE

The fragmentation engine converts suitable habitat into spatial patches.

Pipeline:

```text
Suitability Raster
       ↓
Threshold
       ↓
Binary Habitat Map
       ↓
Connected Component Analysis
       ↓
Habitat Patches
       ↓
Patch Metrics
```

---

# 30. HABITAT PATCH METRICS

Each patch may contain:

```text
area
perimeter
compactness
nearest_patch_distance
suitability
species_relevance
fragmentation_level
```

These values feed into later analysis.

---

# 31. RESISTANCE SURFACE

The resistance surface represents the relative difficulty of moving through landscape cells.

Example conceptual model:

| Landscape             |     Resistance |
| --------------------- | -------------: |
| High-quality habitat  |       Very Low |
| Natural vegetation    |            Low |
| Open/modified habitat |         Medium |
| Agriculture           |           High |
| Major road            |      Very High |
| Dense settlement      | Extremely High |

These are **model parameters**, not universal ecological truths.

They should be configurable.

---

# 32. RESISTANCE ENGINE

```text
Land Cover
   +
Roads
   +
Settlements
   +
Other Barriers
   ↓
Weighted Resistance Model
   ↓
Resistance Raster
```

---

# 33. CONNECTIVITY ENGINE

The connectivity engine identifies potential movement routes between habitat patches.

Possible techniques:

### Least-Cost Path

Finds paths with minimum accumulated resistance.

### Cost-Distance

Calculates movement cost across the landscape.

### Graph Analysis

Represents habitat patches as nodes and potential connections as edges.

For the MVP, the recommended approach is:

> **Resistance surface + least-cost paths + graph representation**

This gives both geographic and analytical outputs.

---

# 34. CONNECTIVITY GRAPH

Conceptual representation:

```text
          Patch A
             ●
            / \
           /   \
          /     \
         ●       ●
      Patch B  Patch C
         \       /
          \     /
             ●
          Patch D
```

Each node represents a habitat patch.

Each edge represents a potential connection.

Edge attributes:

```text
distance
cost
connectivity_score
```

---

# 35. GRAPH ANALYSIS

NetworkX can calculate useful indicators such as:

* degree
* weighted degree
* shortest paths
* centrality
* connected components

This enables WildLink to identify habitat patches that act as important connectors.

---

# 36. CORRIDOR GENERATION

Pipeline:

```text
Habitat Patch A
       +
Habitat Patch B
       ↓
Resistance Surface
       ↓
Cost-Distance
       ↓
Least-Cost Path
       ↓
Candidate Corridor
```

The resulting corridor is stored as geographic geometry.

---

# 37. CONNECTIVITY SCORE

The score should combine measurable characteristics.

Example conceptual model:

```text
Connectivity Score =
Normalized Connection Value
+
Patch Importance
-
Movement Resistance
-
Distance Penalty
```

The exact weights should be configurable and documented.

---

# 38. PRIORITY ENGINE

The priority engine converts analytical outputs into conservation intervention rankings.

Conceptually:

```text
Habitat Value
      +
Connectivity Benefit
      +
Species Relevance
      +
Restoration Opportunity
      -
Constraints
      ↓
Priority Score
```

---

# 39. PRIORITY SCORING MODEL

A normalized weighted model may be used:

```text
Priority =
w1(Habitat)
+
w2(Connectivity)
+
w3(Species)
+
w4(Restoration)
-
w5(Constraint)
```

where:

```text
w1 + w2 + w3 + w4 + w5 = 1
```

The weights should be configurable.

---

# 40. WHY CONFIGURABLE WEIGHTS?

Different conservation objectives may require different priorities.

For example:

### Connectivity-focused

Connectivity gets higher weight.

### Species-focused

Species relevance gets higher weight.

### Restoration-focused

Restoration opportunity gets higher weight.

This makes WildLink more flexible than a single fixed scoring formula.

---

# 41. EXPLAINABILITY ENGINE

The system must store the factors contributing to each recommendation.

Example:

```json
{
  "priority_score": 91,
  "factors": {
    "habitat": 87,
    "connectivity": 94,
    "species": 90,
    "restoration": 88
  },
  "dominant_factor": "connectivity"
}
```

The frontend converts this into a human-readable explanation.

---

# 42. EVIDENCE QUALITY ENGINE

Each result receives an evidence-quality classification.

Potential factors:

```text
data completeness
observation density
dataset age
model confidence
spatial coverage
```

Output:

```text
HIGH
MODERATE
LOW
```

This prevents the system from presenting uncertain outputs as facts.

---

# 43. WHAT-IF SIMULATION ENGINE

This is the signature technical feature.

The engine compares:

```text
BASELINE
   ↓
Intervention
   ↓
Modified Landscape
   ↓
Recalculate Connectivity
   ↓
SIMULATED RESULT
```

---

# 44. SIMULATION INPUT

Example:

```json
{
  "project_id": "123",
  "intervention_type": "habitat_restoration",
  "zone_ids": ["A", "B"],
  "restoration_area": 50,
  "scenario_name": "Scenario A"
}
```

---

# 45. SIMULATION PROCESS

```text
1. Load baseline landscape

2. Load selected intervention zone

3. Modify resistance/suitability assumptions

4. Recalculate affected connectivity

5. Recalculate graph metrics

6. Calculate new connectivity score

7. Compare with baseline

8. Store scenario result
```

---

# 46. SIMULATION OUTPUT

```json
{
  "baseline_connectivity": 42,
  "simulated_connectivity": 63,
  "improvement": 21,
  "percentage_change": 50
}
```

The values are illustrative; actual results must come from the model.

---

# 47. SCENARIO COMPARISON

The frontend should provide:

```text
                    BASELINE
                       42
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
        Zone A        Zone B        Zone C
          49            63            54
          +7            +21           +12
```

The user can immediately understand which scenario provides the greatest modelled improvement.

---

# 48. OPTIMIZATION — FUTURE EXTENSION

A future version can optimize:

```text
Maximum connectivity improvement
subject to
limited restoration budget/area
```

This becomes a constrained optimization problem.

For example:

```text
maximize:
    connectivity_gain

subject to:
    restoration_area ≤ available_area
    cost ≤ available_budget
```

This should remain a future feature unless the team has sufficient development time.

---

# 49. API ARCHITECTURE

All frontend/backend communication occurs through REST APIs.

Base:

```text
/api/v1
```

---

# 50. PROJECT APIs

### Create Project

```http
POST /api/v1/projects
```

### Get Projects

```http
GET /api/v1/projects
```

### Get Project

```http
GET /api/v1/projects/{project_id}
```

### Delete Project

```http
DELETE /api/v1/projects/{project_id}
```

---

# 51. SPECIES APIs

```http
GET /api/v1/species
```

```http
GET /api/v1/species/{species_id}
```

---

# 52. DATASET APIs

```http
POST /api/v1/datasets
```

```http
GET /api/v1/datasets
```

```http
GET /api/v1/datasets/{dataset_id}
```

---

# 53. ANALYSIS APIs

### Habitat

```http
POST /api/v1/analysis/habitat
```

### Fragmentation

```http
POST /api/v1/analysis/fragmentation
```

### Connectivity

```http
POST /api/v1/analysis/connectivity
```

### Priority

```http
POST /api/v1/analysis/priority
```

---

# 54. JOB STATUS API

```http
GET /api/v1/analysis/jobs/{job_id}
```

Example:

```json
{
  "job_id": "abc123",
  "status": "RUNNING",
  "progress": 72
}
```

---

# 55. SIMULATION APIs

### Create Simulation

```http
POST /api/v1/simulations
```

### Get Simulation

```http
GET /api/v1/simulations/{simulation_id}
```

### Compare Scenarios

```http
GET /api/v1/projects/{project_id}/simulations
```

---

# 56. API RESPONSE STANDARD

Every API should follow a consistent structure.

Success:

```json
{
  "success": true,
  "data": {},
  "message": "Analysis completed"
}
```

Error:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REGION",
    "message": "The selected region is invalid."
  }
}
```

---

# 57. API VALIDATION

Use Pydantic schemas for:

* request validation
* response validation
* parameter validation

Reject:

* invalid UUIDs
* invalid geographic boundaries
* impossible numeric values
* malformed scenario parameters

---

# 58. ASYNCHRONOUS ANALYSIS

Spatial processing can be computationally expensive.

The backend should therefore support:

```text
POST analysis
      ↓
Create job
      ↓
Return job ID
      ↓
Worker executes
      ↓
Store result
      ↓
Frontend checks status
```

This prevents request timeouts.

---

# 59. BACKGROUND JOB STATES

```text
QUEUED
   ↓
RUNNING
   ↓
COMPLETED
```

Failure:

```text
RUNNING
   ↓
FAILED
```

The error should be stored for debugging.

---

# 60. CACHING STRATEGY

Repeated analysis should not always be recalculated.

Cache key can include:

```text
project
species
dataset versions
analysis parameters
model version
```

Example:

```text
hash(
project_id +
species_id +
dataset_version +
parameters +
model_version
)
```

If the same analysis exists, reuse the result.

---

# 61. RASTER STORAGE STRATEGY

Large raster datasets should not be transferred directly through standard JSON APIs.

The architecture should instead use:

```text
Raster
 ↓
Storage
 ↓
Tile/visualization layer
 ↓
Map
```

For the hackathon, pre-generated tiles or simplified raster representations can be used if necessary.

---

# 62. GEOJSON STRATEGY

Vector results such as:

* corridors
* priority zones
* habitat patches

can be returned as GeoJSON.

Example:

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": []
  },
  "properties": {
    "priority_score": 91
  }
}
```

---

# 63. SECURITY ARCHITECTURE

Even though the MVP is a hackathon project, security should be designed correctly.

## Authentication

Use token-based authentication.

Possible implementation:

```text
JWT
```

## Authorization

Check project ownership/permissions before returning project data.

---

# 64. SECURITY REQUIREMENTS

Implement:

* password hashing
* JWT expiration
* request validation
* SQL injection protection through ORM/parameterized queries
* CORS restrictions
* rate limiting where appropriate
* secure environment variables
* no secrets in Git
* HTTPS in deployment

---

# 65. ENVIRONMENT VARIABLES

Example:

```text
DATABASE_URL=
JWT_SECRET=
MAP_API_KEY=
STORAGE_BUCKET=
MODEL_PATH=
```

Never hardcode secrets.

Never commit:

```text
.env
```

to GitHub.

---

# 66. LOGGING

Backend logs should include:

```text
timestamp
request_id
endpoint
user/project
operation
duration
status
error
```

Do not log:

* passwords
* tokens
* sensitive credentials

---

# 67. ERROR HANDLING

The backend should distinguish:

### Client Errors

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
422 Validation Error
```

### Server Errors

```text
500 Internal Server Error
```

### Analysis Errors

A failed spatial/ML operation should return a meaningful job error rather than a generic server failure.

---

# 68. FRONTEND ERROR STATES

The UI should handle:

```text
Loading
Empty
Success
Partial Data
Error
Processing
```

Example:

> **Connectivity analysis is processing...**

rather than freezing the interface.

---

# 69. PERFORMANCE TARGETS

For normal dashboard operations:

* API response target: under ~1 second where practical
* map interaction: responsive
* database queries: indexed
* heavy analysis: asynchronous

The team should not promise fixed latency for complex geospatial computations before benchmarking.

---

# 70. SCALABILITY STRATEGY

## Stage 1

One project.

## Stage 2

Multiple projects.

## Stage 3

Multiple species.

## Stage 4

Multiple geographic regions.

## Stage 5

Large-scale conservation intelligence.

Scaling path:

```text
Single Server
     ↓
Containerized Backend
     ↓
Separate Worker
     ↓
Managed PostgreSQL
     ↓
Object Storage
     ↓
Multiple Workers
     ↓
Service Decomposition if required
```

---

# 71. DEPLOYMENT ARCHITECTURE

Recommended:

```text
                 INTERNET
                    │
                    ▼
              HTTPS / Domain
                    │
             ┌──────┴──────┐
             ▼             ▼
        Frontend CDN    API Server
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                PostgreSQL     Worker
                  +PostGIS
                    │
                    ▼
                Data Storage
```

---

# 72. CONTAINERIZATION

Use Docker.

Recommended containers:

```text
frontend
backend
database
worker
```

For the hackathon, frontend hosting and backend hosting may be separate.

---

# 73. DEVELOPMENT ENVIRONMENT

Each developer should be able to run:

```text
Frontend
Backend
Database
Worker
```

using one setup command where possible.

Example conceptual command:

```bash
docker compose up
```

---

# 74. GITHUB REPOSITORY

Recommended structure:

```text
wildlink-ai/
│
├── frontend/
├── backend/
├── ml/
├── geospatial/
├── data/
├── scripts/
├── docs/
├── tests/
├── docker-compose.yml
├── README.md
├── .env.example
└── .gitignore
```

---

# 75. BRANCH STRATEGY

```text
main
 │
 └── develop
      │
      ├── feature/frontend
      ├── feature/backend
      ├── feature/gis
      ├── feature/ml
      └── feature/simulation
```

Keep pull requests small.

Every major feature should be integrated early rather than waiting until the final hours.

---

# 76. TEAM TECHNICAL RESPONSIBILITIES

## MEMBER 1 — You

### AI + GIS + Frontend/Product Lead

Primary ownership:

* frontend
* map interface
* habitat model
* GIS algorithms
* connectivity logic
* priority engine
* simulation logic
* architecture
* demo

Your highest-value role is owning the **intelligence-to-interface pipeline**.

---

# 77. MEMBER 2 — Backend/Data Engineer

Primary ownership:

* FastAPI
* PostgreSQL
* PostGIS
* dataset ingestion
* spatial queries
* database models
* API contracts

---

# 78. MEMBER 3 — Backend/Platform Engineer

Primary ownership:

* analysis APIs
* simulation APIs
* background jobs
* authentication
* deployment
* integration
* testing

---

# 79. TEAM COMMUNICATION CONTRACT

Before development starts, freeze:

### API contracts

Backend developers define endpoints and request/response structures.

### Data contracts

Define exactly what the GIS/ML engine expects.

### UI contracts

Frontend defines what data the map and dashboard require.

This avoids:

> "My backend returns something different from what the frontend expects."

---

# 80. DEVELOPMENT PHASE 1 — FOUNDATION

### Deliverables

* Git repository
* project structure
* React app
* FastAPI app
* PostgreSQL/PostGIS
* Docker environment
* basic map
* API connectivity

### Definition of Done

A user can open the application and see:

```text
Frontend
   ↓
Backend
   ↓
Database
```

working together.

---

# 81. DEVELOPMENT PHASE 2 — DATA PIPELINE

### Deliverables

* selected study region
* species dataset
* habitat dataset
* road/barrier data
* ingestion scripts
* validation

### Definition of Done

Real geographic data appears on the map.

---

# 82. DEVELOPMENT PHASE 3 — HABITAT ANALYSIS

Implement:

```text
features
 ↓
ML model
 ↓
suitability
 ↓
habitat layer
```

### Definition of Done

The system produces a habitat suitability layer.

---

# 83. DEVELOPMENT PHASE 4 — CONNECTIVITY

Implement:

```text
habitat patches
 ↓
resistance
 ↓
least-cost paths
 ↓
corridors
 ↓
graph metrics
```

### Definition of Done

Potential connectivity corridors are displayed on the map.

---

# 84. DEVELOPMENT PHASE 5 — PRIORITY ENGINE

Implement:

```text
habitat
+
connectivity
+
species
+
restoration
 ↓
priority
```

### Definition of Done

The system produces ranked conservation zones.

---

# 85. DEVELOPMENT PHASE 6 — SIMULATION

Implement:

```text
baseline
 ↓
select zone
 ↓
simulate intervention
 ↓
recalculate
 ↓
compare
```

### Definition of Done

The user can compare at least two intervention scenarios.

---

# 86. DEVELOPMENT PHASE 7 — POLISH

Focus on:

* UX
* map clarity
* charts
* explanations
* loading states
* error states
* responsive design

Do not add major new functionality during this phase.

---

# 87. TESTING STRATEGY

Testing must occur at four levels.

## Unit Testing

Test:

* scoring functions
* GIS functions
* data validation
* simulation calculations

## Integration Testing

Test:

```text
Frontend → API → Database
```

## System Testing

Test the complete workflow.

## User Testing

Test whether a person can understand:

* what the map means
* why a zone is prioritized
* what simulation results mean

---

# 88. GIS TESTING

GIS tests should verify:

* valid geometries
* expected intersections
* correct coordinate transformations
* distance calculations
* corridor generation
* area calculations

Spatial tests are particularly important because visually plausible maps can still contain incorrect calculations.

---

# 89. ML TESTING

Verify:

* training data quality
* feature availability
* reproducibility
* model output range
* model performance
* feature importance

Save:

```text
model version
dataset version
parameters
```

with analysis results.

---

# 90. MODEL VERSIONING

Every result should know which model produced it.

Example:

```text
model_version = habitat_rf_v1
dataset_version = landscape_2026_v1
```

This is important when the system is updated.

---

# 91. REPRODUCIBILITY

A conservation analysis should ideally be reproducible.

Store:

```text
project
species
dataset versions
model version
weights
parameters
timestamp
```

Then another analysis can recreate the result.

---

# 92. DATA LINEAGE

For every important result:

```text
Result
 ↓
Model
 ↓
Input dataset
 ↓
Source
```

The user should be able to inspect the source information.

---

# 93. SCIENTIFIC SAFETY

WildLink should explicitly distinguish:

### Observation

Something recorded in the dataset.

### Model Output

Something estimated by an algorithm.

### Simulation

A hypothetical scenario.

The UI should never describe a simulated corridor as:

> "The animal will definitely use this route."

Instead:

> "Potential connectivity corridor under the current model assumptions."

---

# 94. FAILURE MODES

## Dataset unavailable

Display:

> Data source unavailable.

Do not fabricate data.

## Insufficient observations

Display:

> Insufficient observation density for high-confidence modelling.

## Invalid geometry

Reject the dataset or flag the affected records.

## Model failure

Return:

> Analysis could not be completed. Review input data.

## Simulation failure

Preserve the baseline and explain that the scenario could not be evaluated.

---

# 95. OBSERVABILITY

Track:

```text
API latency
analysis duration
job failures
database errors
ML failures
simulation failures
```

For the hackathon, simple structured logs are sufficient.

---

# 96. BACKUP STRATEGY

Production architecture:

* database backups
* object storage backup
* dataset versioning

Hackathon:

* GitHub repository
* local dataset backup
* prepared demo dataset
* exported result snapshots

---

# 97. DEMO RESILIENCE

The final demonstration should not depend entirely on live external data.

Prepare:

```text
Demo Project
Demo Species
Demo Dataset
Precomputed Baseline
Precomputed Analysis
```

The application should still demonstrate the actual analytical pipeline where possible.

---

# 98. HACKATHON MVP TECHNICAL SCOPE

The MVP should contain exactly:

```text
1 Species
1 Region
1 Dataset Pipeline
1 Habitat Model
1 Resistance Model
1 Connectivity Engine
1 Priority Engine
1 Simulation Engine
1 Interactive Map
1 Dashboard
```

This is enough to demonstrate the complete product loop.

---

# 99. WHAT SHOULD NOT BE BUILT DURING THE MVP

Avoid spending hackathon time on:

* mobile application
* multi-language support
* complex user roles
* advanced notification system
* custom IoT
* live wildlife GPS tracking
* complex deep learning
* nationwide data processing
* unnecessary microservices
* complicated DevOps

---

# 100. TECHNICAL DIFFERENTIATOR

WildLink's strongest technical differentiation is the combination of:

```text
Geospatial Data
      +
Machine Learning
      +
Graph Theory
      +
Optimization/Simulation
      +
Explainable Decision Support
```

This is much stronger technically than simply building:

> "An AI chatbot for wildlife."

---

# 101. END-TO-END EXAMPLE

A user selects:

```text
Species:
Target Wildlife Species

Region:
Selected Conservation Landscape
```

The backend retrieves the required datasets.

The GIS engine processes the landscape.

The ML engine estimates suitability.

The fragmentation engine identifies habitat patches.

The resistance engine estimates landscape cost.

The connectivity engine generates candidate corridors.

The priority engine ranks intervention zones.

The user clicks:

```text
Priority Zone #1
```

The system displays:

```text
Priority Score
Habitat Value
Connectivity Value
Species Relevance
Restoration Opportunity
Evidence Quality
```

The user opens:

# What-If Simulator

and selects:

```text
Restore Zone #1
```

The system calculates a new scenario.

The dashboard shows:

```text
Baseline
   ↓
Scenario
   ↓
Estimated Improvement
```

This creates the complete:

> **Data → Intelligence → Decision → Simulation**

workflow.

---

# 102. FINAL TECHNICAL ARCHITECTURE

```text
                         WILDLINK AI
                              │
                              ▼
                     ┌────────────────┐
                     │ React Frontend │
                     └───────┬────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ FastAPI Backend  │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
     Project Layer      Analysis Layer     Simulation Layer
                             │
             ┌───────────────┼────────────────┐
             │               │                │
             ▼               ▼                ▼
         Habitat         GIS Engine       Graph Engine
          Model
             │               │                │
             └───────────────┼────────────────┘
                             ▼
                    Priority Engine
                             │
                             ▼
                    Explainability
                             │
                             ▼
                    PostgreSQL/PostGIS
                             │
                             ▼
                       Data Storage
```

---

# 103. TECHNOLOGY STACK — FINAL

| Layer                 | Technology                      |
| --------------------- | ------------------------------- |
| Frontend              | React                           |
| UI                    | HTML, CSS, JavaScript           |
| Mapping               | Leaflet / MapLibre              |
| Backend               | Python + FastAPI                |
| ORM                   | SQLAlchemy                      |
| Database              | PostgreSQL                      |
| Spatial Database      | PostGIS                         |
| GIS                   | GeoPandas, Shapely, Rasterio    |
| ML                    | scikit-learn                    |
| Graph                 | NetworkX                        |
| API                   | REST                            |
| Background Processing | Worker / Task Queue             |
| Containers            | Docker                          |
| Version Control       | Git + GitHub                    |
| Deployment            | Cloud-hosted frontend + backend |
| Authentication        | JWT                             |
| Data Format           | GeoJSON / CSV / GeoTIFF         |

---

# 104. IMPLEMENTATION PRIORITY

The engineering team should follow this priority:

### P0 — Critical

```text
Database
Backend
Map
Data
Habitat
Connectivity
Priority
```

### P1 — Essential

```text
Simulation
Explanation
Charts
Job Processing
```

### P2 — Polish

```text
Reports
Advanced filters
Authentication refinement
Performance optimization
```

### P3 — Future

```text
Multi-species
Optimization
Historical monitoring
Conflict prediction
Ecosystem health
```

---

# 105. DEFINITION OF DONE

WildLink MVP is considered technically complete when:

### Infrastructure

* [ ] Frontend runs
* [ ] Backend runs
* [ ] Database runs
* [ ] API connection works

### Data

* [ ] Species data loaded
* [ ] Habitat data loaded
* [ ] Barrier data loaded
* [ ] Data validation works

### Intelligence

* [ ] Habitat suitability generated
* [ ] Habitat patches identified
* [ ] Resistance surface generated
* [ ] Corridors generated
* [ ] Priority zones generated

### Simulation

* [ ] Baseline calculated
* [ ] Intervention scenario created
* [ ] Scenario recalculated
* [ ] Comparison displayed

### UI

* [ ] Interactive map works
* [ ] Layers can be toggled
* [ ] Priority zone can be selected
* [ ] Explanation displayed
* [ ] Scenario comparison displayed

### Engineering

* [ ] Git repository organized
* [ ] Environment variables secured
* [ ] Error handling implemented
* [ ] Basic tests completed
* [ ] Demo dataset prepared

---

# 106. FINAL ENGINEERING PRINCIPLE

The architecture should not be judged by how many technologies it contains.

It should be judged by whether the system can reliably perform this sequence:

```text
REAL DATA
   ↓
VALIDATED DATA
   ↓
SPATIAL + ML ANALYSIS
   ↓
CONNECTIVITY MODEL
   ↓
PRIORITIZED INTERVENTION
   ↓
EXPLAINABLE RESULT
   ↓
WHAT-IF SIMULATION
   ↓
BETTER CONSERVATION DECISION
```

That is the technical heart of WildLink AI.

---

# 107. FINAL SYSTEM STATEMENT

> **WildLink AI is architected as a modular AI-GIS conservation intelligence platform in which ecological data is processed through spatial analysis, habitat modelling, resistance-based connectivity analysis and explainable prioritization before being presented through an interactive map and What-If simulation interface.**

The architecture deliberately balances **technical depth, scientific responsibility, scalability and hackathon feasibility**.

The MVP does not attempt to solve all wildlife conservation problems.

It solves one difficult problem exceptionally well:

# **Where should conservation intervention happen first, and what could happen if we intervene there?**

---

## END OF TECHNICAL DESIGN DOCUMENT
