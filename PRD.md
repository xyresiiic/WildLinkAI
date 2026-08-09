# WILDLINK AI

## Product Requirements Document (PRD)

### AI-Powered Wildlife Habitat Connectivity & Conservation Prioritization Platform

**Version:** 1.0
**Product Type:** AI + Geospatial Decision-Support Platform
**Hackathon:** Infinity Hacks 2026
**Track:** Wildlife Conservation
**Primary Users:** Wildlife conservationists, forest departments, researchers, NGOs, conservation planners
**MVP Target:** Hackathon prototype
**Development Team:** 3 members — Product/AI/Frontend Lead + 2 Backend Developers

---

# 1. EXECUTIVE SUMMARY

WildLink AI is a software-based wildlife conservation intelligence platform designed to help conservation teams determine **where conservation intervention should happen first**.

Wildlife habitats are increasingly fragmented by roads, agriculture, settlements, infrastructure and other forms of human activity. While satellite imagery, species observations, land-cover data and biodiversity datasets can provide large amounts of information, raw information alone does not answer the most important conservation question:

> **"If we have limited resources and can intervene in only a few locations, where should we act to create the greatest improvement in wildlife habitat connectivity?"**

WildLink AI addresses this decision-making gap.

The platform combines:

* wildlife species observations
* habitat suitability
* land-cover information
* habitat fragmentation
* human infrastructure
* geographic barriers
* connectivity analysis
* graph-based modelling
* conservation priority scoring
* scenario simulation

to produce an interactive **Conservation Action Intelligence** system.

The platform will identify potential wildlife corridors, rank intervention zones, explain why those areas are important, and allow users to simulate hypothetical restoration scenarios.

The fundamental product philosophy is:

> **Observe → Analyze → Connect → Prioritize → Simulate → Decide**

WildLink is not intended to replace wildlife experts or field research. It is a **decision-support system** that helps experts make more evidence-informed conservation planning decisions.

---

# 2. HACKATHON ALIGNMENT

The selected hackathon track is **Wildlife Conservation**.

The official challenge description encourages solutions involving image recognition and geospatial mapping for tracking wildlife and preventing human-wildlife conflict.

WildLink extends the geospatial aspect into a deeper conservation-planning problem:

> Instead of only showing where wildlife or habitats are located, WildLink determines where conservation intervention may produce the greatest connectivity benefit.

This makes the project directly relevant to the track while introducing a stronger decision-support layer.

The hackathon follows an open-innovation model rather than providing fixed problem statements, allowing teams to identify their own meaningful problem within a selected track.

---

# 3. PRODUCT VISION

## Vision

Build a scalable conservation intelligence platform that transforms fragmented ecological and geospatial data into **explainable, actionable conservation priorities**.

## Long-Term Vision

WildLink should eventually evolve from a habitat-connectivity tool into a broader:

# Conservation Intelligence Platform

with future modules for:

* species population monitoring
* wildlife corridor analysis
* ecosystem health monitoring
* human-wildlife conflict prediction
* biodiversity change detection
* habitat restoration planning
* climate-impact analysis
* conservation resource optimization

However, these features are deliberately outside the initial MVP.

---

# 4. PROBLEM STATEMENT

## 4.1 Core Problem

Wildlife populations require connected habitats for:

* movement
* feeding
* breeding
* migration
* access to water
* genetic exchange
* long-term population resilience

Human development increasingly fragments these habitats.

A landscape may contain multiple high-quality habitat patches, but roads, settlements, agriculture and other barriers may prevent effective movement between them.

This produces a critical conservation challenge:

> **Which fragmented areas should be protected or restored first to maximize ecological connectivity?**

---

# 5. PROBLEM BREAKDOWN

The problem consists of five connected sub-problems.

## 5.1 Habitat Identification

Where are the areas that provide suitable conditions for a target species?

## 5.2 Habitat Fragmentation

How fragmented are these suitable areas?

## 5.3 Connectivity

Which habitat patches could potentially be connected?

## 5.4 Conservation Prioritization

Which locations offer the greatest conservation value?

## 5.5 Resource Optimization

If only limited land, money or restoration capacity is available, which intervention should be prioritized?

Existing systems may solve one or more of these problems individually.

WildLink's goal is to connect them into one decision-support workflow.

---

# 6. TARGET USERS

## Primary Users

### 1. Forest & Wildlife Departments

Use WildLink for:

* habitat planning
* corridor identification
* restoration prioritization
* landscape analysis

### 2. Conservation NGOs

Use the platform to:

* identify priority restoration zones
* support conservation proposals
* prioritize limited funding
* visualize ecological evidence

### 3. Wildlife Researchers

Use WildLink to:

* study habitat connectivity
* analyze species observations
* evaluate landscape fragmentation
* compare scenarios

### 4. Conservation Planners

Use WildLink to compare possible intervention strategies.

### 5. Environmental Organizations

Use the platform for evidence-based landscape planning.

---

# 7. USER PERSONA

## Conservation Planner

**Goal:**

Determine where limited conservation resources should be allocated.

**Current difficulty:**

Data exists across multiple sources and tools.

**Needs:**

* geographic visualization
* species-specific analysis
* connectivity assessment
* priority ranking
* evidence behind recommendations
* scenario comparison

**Desired outcome:**

> "I know which area should receive priority and why."

---

# 8. PRODUCT OBJECTIVES

## Primary Objectives

### Objective 1

Identify suitable wildlife habitat.

### Objective 2

Measure landscape fragmentation.

### Objective 3

Identify potential habitat connectivity pathways.

### Objective 4

Rank conservation intervention zones.

### Objective 5

Explain why each zone receives its priority score.

### Objective 6

Allow users to simulate hypothetical restoration scenarios.

### Objective 7

Compare the expected connectivity benefit of different interventions.

---

# 9. SUCCESS CRITERIA

The MVP is successful if a user can:

1. select a study region
2. select a target species
3. load relevant ecological/geospatial data
4. generate habitat suitability information
5. identify fragmented habitat
6. identify potential connectivity pathways
7. obtain ranked intervention zones
8. understand why a zone is prioritized
9. create a restoration scenario
10. compare the simulated outcome against the baseline

---

# 10. CORE PRODUCT PRINCIPLE

WildLink must not become:

> **"Another wildlife dashboard."**

The product should answer:

> **"What should we do next?"**

Therefore every major analysis should ultimately contribute to a decision.

---

# 11. PRODUCT WORKFLOW

```text
                DATA SOURCES
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
 Species Data   Habitat Data   Human Activity
       │             │             │
       └─────────────┼─────────────┘
                     ▼
             DATA PROCESSING
                     │
                     ▼
           HABITAT SUITABILITY
                     │
                     ▼
           FRAGMENTATION MODEL
                     │
                     ▼
          CONNECTIVITY ANALYSIS
                     │
                     ▼
          PRIORITY SCORE ENGINE
                     │
                     ▼
          CONSERVATION MAP
                     │
                     ▼
         WHAT-IF SIMULATOR
                     │
                     ▼
          ACTION RECOMMENDATION
```

---

# 12. CORE FEATURES

## F1 — Study Area Selection

Users can define a geographic study area.

### Inputs

* map selection
* predefined study regions
* uploaded geographic boundary where supported

### Output

A selected geographic analysis region.

---

# 13. F2 — Species Selection

The user selects a target species.

Example:

* Tiger
* Elephant
* Leopard
* other species depending on dataset availability

The system should associate species-specific analysis with the selected region.

---

# 14. F3 — Species Observation Layer

Display available species occurrence information.

Each observation can contain:

* species
* geographic coordinates
* observation date
* data source
* confidence where available

Map representation:

```text
● ●       ●

      ●

   ●          ●

        ●
```

The user can visually understand species distribution.

---

# 15. F4 — Habitat Suitability Analysis

The system estimates the suitability of areas for the selected species.

Potential input factors:

* land cover
* vegetation
* water proximity
* protected areas
* species observations
* terrain/environmental variables where available

Output:

### Habitat Suitability Score

Example:

```text
90–100  Highly Suitable
70–89   Suitable
50–69   Moderate
30–49   Low
0–29    Unsuitable
```

The thresholds should remain configurable rather than hardcoded into the product concept.

---

# 16. F5 — Habitat Fragmentation Analysis

The system identifies isolated habitat patches.

Metrics may include:

* patch area
* distance between patches
* habitat density
* fragmentation level
* barrier proximity

The platform should visualize fragmented areas.

Example:

```text
████████       ███████
Habitat A      Habitat B

      ROAD
──────────────────────

██████
Habitat C
```

---

# 17. F6 — Resistance Surface

A resistance surface represents how difficult movement through different landscape types may be.

Conceptual example:

| Landscape        | Relative Resistance |
| ---------------- | ------------------: |
| Natural habitat  |                 Low |
| Grassland        |          Low/Medium |
| Agriculture      |              Medium |
| Roads            |                High |
| Dense settlement |           Very High |

These values must be treated as modelling assumptions and should ideally be configurable.

The system must clearly communicate that resistance values are model parameters rather than direct measurements of animal movement.

---

# 18. F7 — Connectivity Analysis

The system calculates potential connections between habitat patches.

Possible methods include:

* least-cost path
* cost-distance analysis
* graph-based connectivity
* corridor scoring
* resistance-based routing

The system generates candidate corridors.

Example:

```text
Habitat A
████████
    \
     \
      \\\\\\\\\
               \
                ████████
                Habitat B
```

---

# 19. F8 — Conservation Priority Engine

This is one of the most important components.

The engine ranks candidate intervention zones.

A conceptual priority model:

```text
Priority Score
=
Habitat Value
+
Connectivity Benefit
+
Species Relevance
+
Restoration Opportunity
-
Environmental Constraints
```

A production version should use normalized values and configurable weights.

---

# 20. PRIORITY SCORE EXAMPLE

### Zone A

Habitat suitability: 82
Connectivity potential: 65
Species relevance: 76
Restoration opportunity: 70

### Zone B

Habitat suitability: 87
Connectivity potential: 94
Species relevance: 90
Restoration opportunity: 88

### Zone C

Habitat suitability: 91
Connectivity potential: 52
Species relevance: 82
Restoration opportunity: 60

The system could rank:

```text
#1 Zone B
#2 Zone A
#3 Zone C
```

The platform must explain the ranking.

---

# 21. F9 — Explainable Recommendation

Every recommendation should answer:

### WHAT?

Zone B is the highest priority.

### WHY?

Because it:

* connects major habitat patches
* has high habitat suitability
* provides high potential connectivity improvement
* has meaningful species relevance

### CONFIDENCE?

Based on:

* data quality
* observation density
* model confidence
* input completeness

This prevents the system from becoming an unexplained "AI says so" application.

---

# 22. F10 — WHAT-IF CONSERVATION SIMULATOR

## Core USP

The user can simulate a hypothetical restoration intervention.

Example:

### Baseline

Connectivity:

**42**

### Scenario A

Restore Zone A:

**49**

Improvement:

**+7**

### Scenario B

Restore Zone B:

**63**

Improvement:

**+21**

### Scenario C

Restore Zone C:

**54**

Improvement:

**+12**

The system recommends:

> **Zone B provides the highest estimated connectivity improvement under the selected scenario assumptions.**

---

# 23. RESOURCE-CONSTRAINED SIMULATION

A more advanced version allows:

### User input

Available restoration area:

**50 hectares**

The system evaluates possible intervention combinations.

Conceptually:

```text
50 hectares available
        ↓
Candidate zones
        ↓
Connectivity simulation
        ↓
Optimization
        ↓
Best intervention combination
```

This introduces an optimization component.

For the hackathon MVP, this can initially be simplified to comparing a small number of predefined candidate scenarios.

---

# 24. F11 — Scenario Comparison

Users should be able to compare:

| Scenario |  Area | Connectivity | Improvement |
| -------- | ----: | -----------: | ----------: |
| Baseline |  0 ha |           42 |           — |
| Zone A   | 50 ha |           49 |          +7 |
| Zone B   | 50 ha |           63 |     **+21** |
| Zone C   | 50 ha |           54 |         +12 |

This is an excellent visualization for the final demo.

---

# 25. F12 — Interactive Conservation Map

The map is the primary interface.

Possible layers:

* habitat suitability
* species observations
* habitat patches
* potential corridors
* fragmentation
* roads
* settlements
* protected areas
* priority zones

Users can toggle layers.

---

# 26. F13 — Priority Zone Details

When the user clicks a zone:

### Zone B

**Priority:** Critical

**Score:** 91/100

**Connectivity:** Very High

**Habitat Suitability:** High

**Fragmentation:** High

**Restoration Opportunity:** High

### Explanation

> This zone connects two high-value habitat patches and has high estimated connectivity benefit under the current model.

---

# 27. F14 — Evidence Quality

Every analysis should display an evidence indicator.

Example:

### Evidence Quality

**Moderate**

Because:

* species observations are limited
* habitat data is available
* road data is available
* historical information is incomplete

This is scientifically more responsible than presenting predictions as absolute facts.

---

# 28. AI/ML REQUIREMENTS

AI should be used where it improves the product.

Potential ML tasks:

### Habitat suitability modelling

Possible models:

* Random Forest
* Gradient Boosting
* Logistic Regression

For a hackathon, prioritize:

**interpretable + fast + reliable**

over:

**complex + difficult to validate.**

---

# 29. AI EXPLAINABILITY

The system should be able to provide feature-level reasoning.

Example:

> Zone B received a high suitability score because it is close to known species observations, contains suitable land-cover characteristics, and has favourable habitat conditions.

This explanation should be generated from actual model features, not fabricated by an LLM.

An LLM, if included, should assist with natural-language summaries rather than determine the underlying ecological result.

---

# 30. GEOSPATIAL ENGINE

The GIS layer is central to WildLink.

Potential technologies:

* GeoPandas
* Rasterio
* Shapely
* NetworkX
* PostGIS

Responsibilities:

* spatial joins
* geometry processing
* raster analysis
* distance calculations
* intersection analysis
* corridor modelling
* graph construction

---

# 31. DATA SOURCES

The MVP should use credible publicly available data.

Potential sources:

* biodiversity occurrence datasets
* protected-area boundaries
* land-cover data
* satellite-derived environmental data
* road networks
* settlement information
* species observation datasets

The team should document every dataset and its source.

---

# 32. DATA STRATEGY

The project must NOT attempt to model the entire planet.

Recommended MVP:

### One region

*

### One focal species

*

### Limited but reliable variables

*

### One clear conservation decision

For example:

> **Habitat connectivity analysis for a selected wildlife species in a selected Indian landscape.**

The exact species and region should be finalized only after checking data availability.

---

# 33. DATA QUALITY REQUIREMENTS

The system should detect or flag:

* missing coordinates
* duplicate observations
* invalid geometries
* insufficient observations
* missing environmental data
* outdated records

Bad data should not silently produce a high-confidence recommendation.

---

# 34. SYSTEM ARCHITECTURE

```text
                         USER
                          │
                          ▼
                 React Web Application
                          │
                          ▼
                     REST API
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
     Project API     Analysis API     Simulation API
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                 Intelligence Layer
                          │
          ┌───────────────┼─────────────────┐
          ▼               ▼                 ▼
       ML Engine       GIS Engine       Graph Engine
          │               │                 │
          └───────────────┼─────────────────┘
                          ▼
                   PostgreSQL/PostGIS
                          │
                          ▼
                    Data Storage
```

---

# 35. TECHNOLOGY STACK

## Frontend

* React
* JavaScript
* HTML/CSS
* Leaflet or MapLibre
* charting library where necessary

## Backend

* Python
* FastAPI

## Database

* PostgreSQL
* PostGIS

## AI/ML

* Python
* scikit-learn

## Geospatial

* GeoPandas
* Rasterio
* Shapely

## Graph/Connectivity

* NetworkX

## Infrastructure

* Docker
* Git/GitHub

The architecture should remain modular so that individual components can be replaced later.

---

# 36. API DESIGN

Potential APIs:

```text
POST /api/projects

GET /api/projects/{project_id}

GET /api/species

GET /api/regions

POST /api/analysis/habitat

POST /api/analysis/fragmentation

POST /api/analysis/connectivity

POST /api/analysis/priority

GET /api/zones

GET /api/zones/{zone_id}

POST /api/simulations

GET /api/simulations/{simulation_id}

GET /api/scenarios/{project_id}
```

The final API contract should be frozen before frontend integration.

---

# 37. DATABASE DESIGN

## User

```text
id
name
email
role
created_at
```

## Project

```text
id
name
region
species_id
created_at
```

## Species

```text
id
common_name
scientific_name
```

## Observation

```text
id
species_id
location
observed_at
source
confidence
```

## Habitat Zone

```text
id
project_id
geometry
suitability_score
```

## Corridor

```text
id
project_id
geometry
connectivity_score
```

## Priority Zone

```text
id
project_id
geometry
priority_score
explanation
evidence_quality
```

## Simulation

```text
id
project_id
scenario_parameters
baseline_score
simulated_score
improvement
created_at
```

---

# 38. NON-FUNCTIONAL REQUIREMENTS

## Performance

The UI should remain responsive during normal map interaction.

Long-running spatial analyses should execute asynchronously rather than blocking API requests.

## Reliability

The system should gracefully handle:

* missing data
* invalid regions
* analysis failures
* empty results

## Security

Implement:

* secure authentication
* authorization
* input validation
* secure secret management
* API protection
* database access controls

## Maintainability

Code should be modular and documented.

## Scalability

The system should allow multiple projects and geographic regions.

---

# 39. FRONTEND INFORMATION ARCHITECTURE

```text
WildLink
│
├── Dashboard
│
├── Projects
│   ├── Project List
│   └── Project Details
│
├── Analysis
│   ├── Habitat
│   ├── Fragmentation
│   └── Connectivity
│
├── Conservation Map
│
├── Priority Zones
│
├── What-If Simulator
│
└── Reports
```

For the hackathon, not all sections need to become separate pages.

A single analysis workspace can contain most functionality.

---

# 40. PRIMARY DASHBOARD

The dashboard should answer four questions immediately:

### Where?

Selected study region.

### What?

Selected species.

### How healthy?

Habitat/connectivity indicators.

### What should we do?

Top conservation priorities.

Example:

```text
┌─────────────────────────────────────┐
│ WildLink AI                         │
│                                     │
│ Region: Selected Landscape          │
│ Species: Tiger                      │
│                                     │
│ Habitat       Connectivity          │
│ 78/100        42/100                │
│                                     │
│ Priority Zones: 12                  │
│ Critical: 3                         │
│                                     │
│          [ OPEN MAP ]               │
└─────────────────────────────────────┘
```

---

# 41. MAP EXPERIENCE

The map should be the heart of the product.

Use clear visual hierarchy.

### Base layer

Geographic map.

### Analytical layers

* habitat
* species
* fragmentation
* corridors
* priority

### Interaction

Clicking an object opens contextual information.

---

# 42. USER JOURNEY

### Before WildLink

User has:

* multiple datasets
* static maps
* spreadsheets
* fragmented evidence

and must manually determine where to intervene.

### With WildLink

```text
Select Species
      ↓
Select Region
      ↓
Analyze
      ↓
View Habitat
      ↓
View Connectivity
      ↓
See Priorities
      ↓
Run Scenario
      ↓
Compare
      ↓
Make Decision
```

---

# 43. MVP SCOPE

## MUST HAVE

1. Geographic study area
2. Species selection
3. Species observations
4. Habitat suitability
5. Fragmentation visualization
6. Connectivity modelling
7. Priority zones
8. Explainable scoring
9. What-If simulation
10. Interactive map
11. Backend API
12. Spatial database

---

# 44. SHOULD HAVE

* ML-based habitat suitability
* multiple species
* scenario comparison
* evidence-quality indicator
* downloadable report
* historical comparison

---

# 45. FUTURE FEATURES

These should NOT compromise the MVP.

Potential future additions:

* population estimation
* camera-trap image analysis
* ecosystem health
* acoustic biodiversity monitoring
* human-wildlife conflict prediction
* climate-change impact
* wildfire risk
* restoration monitoring
* conservation budget optimization
* mobile field application

---

# 46. OUT OF SCOPE FOR HACKATHON MVP

Explicitly exclude:

* custom IoT hardware
* custom wildlife tracking devices
* drone integration
* nationwide real-time monitoring
* full-scale ecological simulation
* production government deployment
* guaranteed animal movement prediction
* automatic conservation decisions

The platform is a **decision-support prototype**, not a fully deployed ecological management system.

---

# 47. TEAM RESPONSIBILITIES

## MEMBER 1 — YOU

### Product + AI/ML + GIS + Frontend Lead

Responsibilities:

* product architecture
* problem definition
* AI/ML
* habitat suitability
* connectivity methodology
* scoring model
* GIS visualization
* frontend
* UX
* presentation
* technical documentation

You should own the **intelligence layer + product experience**.

---

# 48. MEMBER 2

## Backend + Data Engineer

Responsibilities:

* FastAPI
* PostgreSQL
* PostGIS
* data ingestion
* preprocessing
* spatial queries
* API implementation
* data validation

---

# 49. MEMBER 3

## Backend + Platform Engineer

Responsibilities:

* analysis APIs
* simulation engine integration
* job processing
* authentication
* database integration
* deployment
* frontend/backend integration
* testing

---

# 50. GIT/GITHUB STRUCTURE

Recommended:

```text
wildlink-ai/
│
├── frontend/
│
├── backend/
│
├── ml/
│
├── geospatial/
│
├── data/
│
├── docs/
│
├── scripts/
│
├── tests/
│
├── docker/
│
├── README.md
└── .gitignore
```

Branches:

```text
main
develop
feature/frontend
feature/backend
feature/gis
feature/ml
feature/simulation
```

For a 48-hour hackathon, keep the workflow lightweight and avoid complicated Git processes.

---

# 51. DEVELOPMENT PHASES

## Phase 0 — Preparation

Before the official development period:

* finalize species
* finalize geographic region
* research datasets
* finalize architecture
* create repository
* create wireframes
* prepare task board

The hackathon rules state that project building must occur during the official 15–16 August development period, although structuring can begin by 14 August.

---

# 52. PHASE 1 — FOUNDATION

### Goal

Get the system running.

Build:

* repository
* frontend
* backend
* database
* basic map
* API connection

---

# 53. PHASE 2 — DATA

Build:

* dataset ingestion
* cleaning
* spatial processing
* database loading

Output:

**Real data visible on the map.**

---

# 54. PHASE 3 — INTELLIGENCE

Implement:

1. habitat suitability
2. fragmentation
3. connectivity
4. priority scoring

This is the most important technical phase.

---

# 55. PHASE 4 — SIMULATION

Implement:

```text
Baseline
   ↓
Select intervention
   ↓
Modify landscape model
   ↓
Recalculate connectivity
   ↓
Compare results
```

---

# 56. PHASE 5 — UI

Polish:

* map
* priority panel
* analysis results
* simulation interface
* charts
* explanations

---

# 57. PHASE 6 — TESTING

Test:

* API
* database
* geographic boundaries
* invalid data
* missing data
* analysis failures
* simulation edge cases
* frontend responsiveness

---

# 58. PHASE 7 — DEMO

Create a deterministic demonstration.

Do not depend on:

* live external APIs
* unpredictable model outputs
* unstable internet services

The demo dataset should be prepared and cached where possible.

---

# 59. 48-HOUR EXECUTION PRIORITY

## First 6 hours

Architecture + data + repository + basic backend/frontend.

## 6–18 hours

Data pipeline + map + habitat analysis.

## 18–30 hours

Connectivity + priority engine.

## 30–38 hours

What-If Simulator.

## 38–43 hours

Integration + testing.

## 43–46 hours

UI polish + demo workflow.

## 46–48 hours

Pitch + documentation + final testing.

---

# 60. DEMO SCENARIO

The demo should follow one story.

## Opening

> "A conservation team has enough resources to restore only one area. Which location should receive priority?"

Show a fragmented landscape.

Then select the target species.

Run WildLink.

The map reveals several habitat patches.

Then activate:

**Connectivity Analysis**

Potential corridors appear.

Next:

**Priority Analysis**

The system identifies:

### Zone B — Priority #1

Then open the explanation:

> High connectivity potential + high species relevance + significant fragmentation + high restoration opportunity.

Then launch:

# What-If Simulator

Restore Zone B.

Show:

```text
Baseline connectivity
42

After intervention
63

Estimated improvement
+21%
```

Then compare another zone.

Finally:

> **"WildLink doesn't just tell conservationists what exists. It helps them decide where limited conservation effort may create the greatest connectivity benefit."**

---

# 61. PRIMARY USP

## Existing approach

```text
Data
 ↓
Map
 ↓
Human interpretation
```

## WildLink

```text
Data
 ↓
AI/GIS Analysis
 ↓
Connectivity Model
 ↓
Priority Ranking
 ↓
Scenario Simulation
 ↓
Decision Support
```

The differentiation is not simply "AI."

The differentiation is:

# **Evidence-backed conservation prioritization + intervention simulation.**

---

# 62. INNOVATION CLAIM

The project should avoid making unsupported claims such as:

> "No existing platform does this."

Instead state:

> "WildLink integrates habitat suitability, fragmentation, connectivity modelling and conservation prioritization into a single decision-support workflow, with an interactive What-If simulator designed to compare potential restoration interventions."

That is a defensible innovation statement.

---

# 63. SCIENTIFIC RESPONSIBILITY

WildLink must distinguish between:

### Observed data

What has actually been recorded.

### Modelled result

What the algorithm estimates.

### Scenario result

What the model predicts under a hypothetical intervention.

The UI should make this distinction clear.

For example:

**Observed:** 143 species observations

**Modelled:** Habitat suitability 82/100

**Scenario:** Estimated connectivity improvement +21%

Never present a simulation as a guaranteed ecological outcome.

---

# 64. LIMITATIONS

The MVP may have:

* limited species data
* incomplete observation coverage
* simplified resistance values
* simplified ecological assumptions
* limited historical data
* model uncertainty

These should be disclosed.

This actually strengthens the project because it demonstrates scientific maturity.

---

# 65. RISK REGISTER

| Risk                        | Severity | Mitigation                      |
| --------------------------- | -------- | ------------------------------- |
| Poor dataset                | High     | Validate datasets early         |
| GIS complexity              | High     | Use simplified MVP model        |
| ML accuracy                 | Medium   | Use interpretable models        |
| Backend integration failure | High     | Define APIs early               |
| Simulation too complex      | High     | Start with predefined scenarios |
| UI takes too long           | Medium   | Build functional UI first       |
| External API failure        | High     | Cache demo data                 |
| Scope explosion             | Critical | One species + one region        |

---

# 66. PRODUCT METRICS

## Technical

* processing success rate
* analysis latency
* API reliability
* model validation metrics

## Product

* time to identify priority zone
* scenario comparison time
* explanation clarity

## Conservation

Potential metrics:

* connected habitat area
* number of habitat patches connected
* estimated connectivity improvement
* intervention priority score

These metrics should be presented as **model-derived indicators**, not guaranteed ecological outcomes.

---

# 67. SCALABILITY

### Stage 1

One species + one landscape.

### Stage 2

Multiple species.

### Stage 3

Multiple protected areas.

### Stage 4

Regional conservation planning.

### Stage 5

National conservation intelligence.

The architecture should therefore separate:

* data ingestion
* analysis
* modelling
* visualization

so new datasets and models can be added without rewriting the platform.

---

# 68. FUTURE PRODUCT ARCHITECTURE

```text
                    WILDLINK
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   Habitat AI       Species AI      Ecosystem AI
       │               │                │
       └───────────────┼────────────────┘
                       ▼
               Conservation Engine
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Priority      Simulation     Risk
       Engine         Engine       Engine
          │            │            │
          └────────────┼────────────┘
                       ▼
                Decision Support
```

---

# 69. JUDGING STRATEGY

Infinity Hacks Round 1 evaluates:

* Problem Understanding
* Innovation
* Technical Approach
* Feasibility
* Scalability
* Presentation Quality
* Potential Impact.

WildLink should therefore deliberately address every criterion.

### Problem Understanding

Explain habitat fragmentation and limited conservation resources.

### Innovation

Emphasize integrated prioritization + What-If simulation.

### Technical Approach

Show:

GIS + ML + graph algorithms + optimization + backend architecture.

### Feasibility

Show one species + one region + real datasets.

### Scalability

Explain multi-species/multi-region architecture.

### Presentation

Use the interactive map as the visual centerpiece.

### Impact

Show how the platform could help prioritize conservation intervention.

---

# 70. ROUND 1 PRESENTATION STRUCTURE

The hackathon requires **8–12 slides** and specifies sections including problem, solution, working approach, technology stack, innovation, target users, feasibility, scalability and timeline.

Recommended WildLink deck:

### Slide 1

**WildLink AI**

One-line problem/solution.

### Slide 2

**The Problem**

Habitat fragmentation + limited conservation resources.

### Slide 3

**Why Existing Approaches Are Insufficient**

Data exists, but decision-making remains fragmented.

### Slide 4

**Our Solution**

WildLink architecture.

### Slide 5

**How It Works**

Data → Habitat → Connectivity → Priority.

### Slide 6

**The USP**

What-If Conservation Simulator.

### Slide 7

**Technical Architecture**

Frontend + backend + GIS + ML + PostGIS.

### Slide 8

**Example**

One real geographic scenario.

### Slide 9

**Feasibility + Roadmap**

48-hour implementation.

### Slide 10

**Impact + Scalability**

Future conservation intelligence platform.

---

# 71. SOP ALIGNMENT

The mandatory SOP must explain the team, problem, solution, motivation, technical approach, innovation, feasibility, expected impact and future scope, with a recommended maximum of two pages.

The PRD therefore provides the underlying material, but the final SOP should be rewritten in your team's own voice.

The hackathon rules explicitly state that AI tools may assist but the submission should reflect the team's own understanding and ideas.

---

# 72. FINAL PRODUCT DEFINITION

## Product Name

**WildLink AI**

## Category

AI + Geospatial Conservation Intelligence

## Core Problem

Wildlife habitat fragmentation makes conservation planning difficult, while resources for restoration are limited.

## Core Solution

A platform that analyzes habitat suitability, fragmentation, species relevance and landscape connectivity to identify high-priority conservation intervention zones.

## Signature Feature

**What-If Conservation Simulator**

## Core Output

> **Where should conservation intervention happen first, and why?**

## Primary Technology

Python + FastAPI + PostgreSQL/PostGIS + React + GIS + ML + graph algorithms.

## Primary MVP

One species + one landscape + one conservation decision.

## Long-Term Vision

A scalable conservation intelligence platform.

---

# 73. THE ONE-SENTENCE PRODUCT PITCH

> **WildLink AI transforms wildlife and geospatial data into actionable conservation intelligence by identifying where habitat restoration can potentially create the greatest connectivity benefit and allowing conservation planners to simulate and compare intervention scenarios before allocating limited resources.**

---

# 74. FINAL PRODUCT PRINCIPLE

Every feature in WildLink must pass one question:

> **"Does this help a conservation decision-maker understand where to act, why to act there, or what could happen if they act?"**

If the answer is **no**, it does not belong in the MVP.

# WILDLINK AI

### Observe.

### Analyze.

### Connect.

### Prioritize.

### Simulate.

### Protect.
