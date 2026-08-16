"""
WildLink AI — Comprehensive System-Wide Test Suite
Tests every engine, API endpoint, database transaction, simulation, and export service.
"""
import sys
import os
import time

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from starlette.testclient import TestClient
from app.main import app

def run_tests():
    print("=" * 70)
    print(">> WILDLINK AI -- COMPREHENSIVE END-TO-END SYSTEM TEST SUITE")
    print("=" * 70)

    client = TestClient(app)
    passed_tests = 0
    total_tests = 0

    def test(name, func):
        nonlocal passed_tests, total_tests
        total_tests += 1
        print(f"\n[{total_tests}] Testing: {name}...")
        try:
            func()
            print(f"    [PASS] {name}")
            passed_tests += 1
        except AssertionError as e:
            print(f"    [FAIL] {name} - Assertion Error: {e}")
        except Exception as e:
            print(f"    [ERROR] {name} - Exception: {e}")

    # 1. Health & Root Endpoint
    def test_health():
        res = client.get("/api/v1/health")
        assert res.status_code == 200, f"Status: {res.status_code}"
        data = res.json()
        assert data.get("status") == "healthy" or data.get("success") == True, f"Data: {data}"
    test("Health Check Endpoint (/api/v1/health)", test_health)

    # 2. Species Catalog
    species_list = []
    def test_species():
        nonlocal species_list
        res = client.get("/api/v1/species")
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") == True
        species_list = data.get("data", [])
        assert len(species_list) == 7, f"Expected 7 species, found {len(species_list)}"
        names = [s["common_name"] for s in species_list]
        for expected in ["Bengal Tiger", "Indian Elephant", "Snow Leopard", "Gharial"]:
            assert expected in names, f"Missing {expected}"
    test("Species Catalog Listing (/api/v1/species)", test_species)

    # 3. Project Creation
    project_id = None
    target_species = None
    def test_project_create():
        nonlocal project_id, target_species
        target_species = species_list[0]
        res = client.post("/api/v1/projects", json={
            "name": f"Automated Test Suite Project - {target_species['common_name']}",
            "description": "Integration test project for full stack verification",
            "region_name": "Central Indian Highlands",
            "species_id": target_species["id"]
        })
        assert res.status_code in (200, 201), f"Status: {res.status_code}"
        data = res.json()
        assert data.get("success") == True
        project_id = data["data"]["id"]
        assert project_id is not None
    test("Project Creation (/api/v1/projects)", test_project_create)

    # 4. Species Observations
    def test_observations():
        res = client.get(f"/api/v1/analysis/observations/{project_id}")
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") == True
        obs_data = data.get("data", {})
        assert obs_data.get("count", 0) > 0, "Expected observations to be present"
        assert len(obs_data.get("features", [])) == obs_data.get("count")
    test("Observations Retrieval (/api/v1/analysis/observations/{id})", test_observations)

    # 5. Full Pipeline Analysis Execution
    job_id = None
    def test_run_analysis():
        nonlocal job_id
        res = client.post("/api/v1/analysis/run", json={
            "project_id": project_id,
            "type": "full",
            "parameters": {
                "weights": {
                    "habitat": 0.25,
                    "connectivity": 0.30,
                    "species": 0.20,
                    "restoration": 0.15,
                    "constraint": 0.10
                }
            }
        })
        assert res.status_code == 202, f"Status: {res.status_code}"
        data = res.json()
        assert data.get("success") == True
        job_id = data["data"]["id"]

        # Poll until complete
        for _ in range(120):
            time.sleep(0.5)
            poll_res = client.get(f"/api/v1/analysis/jobs/{job_id}").json()
            if poll_res.get("success"):
                status = poll_res["data"]["status"]
                if status == "completed":
                    return
                elif status == "failed":
                    raise AssertionError(f"Job failed with error: {poll_res['data'].get('error')}")
        raise TimeoutError("Analysis job timed out")
    test("Full Pipeline Execution (/api/v1/analysis/run)", test_run_analysis)

    # 6. Habitat Zones Retrieval & Validation
    def test_habitat_zones():
        res = client.get(f"/api/v1/analysis/habitat/{project_id}")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["count"] > 100, f"Expected >100 habitat zones, got {data['count']}"
        feat = data["features"][0]
        assert "geometry" in feat and feat["geometry"]["type"] == "Polygon"
        assert "suitability_score" in feat["properties"]
        assert "area_hectares" in feat["properties"]
    test("Habitat Zones Feature Validation", test_habitat_zones)

    # 7. Corridors & Graph Connectivity
    def test_corridors():
        res = client.get(f"/api/v1/analysis/corridors/{project_id}")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["count"] > 0, "Expected corridors to be generated"
        feat = data["features"][0]
        assert feat["geometry"]["type"] == "LineString"
        assert feat["properties"]["connectivity_score"] > 0
        assert feat["properties"]["length_km"] > 0
    test("Corridors & Least-Cost Paths Validation", test_corridors)

    # 8. Multi-Criteria Priority Scoring
    def test_priority_zones():
        res = client.get(f"/api/v1/analysis/priority/{project_id}")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["count"] > 0, "Expected priority zones to be generated"
        feat = data["features"][0]
        props = feat["properties"]
        assert props["rank"] == 1
        assert "priority_score" in props
        assert "dominant_factor" in props
        assert "explanation" in props and len(props["explanation"]) > 10
    test("Priority Ranking & AI Explanation Engine", test_priority_zones)

    # 9. What-If Simulation Scenario
    def test_simulation():
        res = client.post("/api/v1/simulations", json={
            "project_id": project_id,
            "name": "Integration Test Habitat Restoration Scenario",
            "intervention_type": "habitat_restoration",
            "parameters": {"intensity": 1.3}
        })
        assert res.status_code == 202
        sim_id = res.json()["data"]["id"]

        # Poll simulation
        sim_data = None
        for _ in range(60):
            time.sleep(0.5)
            s_res = client.get(f"/api/v1/simulations/{sim_id}").json()
            if s_res.get("success") and s_res["data"]["status"] == "completed":
                sim_data = s_res["data"]
                break
            elif s_res.get("success") and s_res["data"]["status"] == "failed":
                raise AssertionError("Simulation status failed")

        assert sim_data is not None, "Simulation did not complete in time"
        assert sim_data["simulated_connectivity"] > sim_data["baseline_connectivity"]
        assert sim_data["improvement"] > 0
        assert sim_data["percentage_change"] > 0
    test("What-If Simulation Scenario (/api/v1/simulations)", test_simulation)

    # 10. Dashboard Analytics Aggregations
    def test_dashboard():
        res = client.get(f"/api/v1/projects/{project_id}/dashboard")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["project_name"] is not None
        assert data["total_habitat_patches"] > 0
        assert data["total_corridors"] > 0
        assert data["total_priority_zones"] > 0
        assert data["habitat_score"] is not None
    test("Dashboard Metrics Aggregations (/api/v1/projects/{id}/dashboard)", test_dashboard)

    # 11. Project Conservation Data Export
    def test_export():
        res = client.get(f"/api/v1/projects/{project_id}/export")
        assert res.status_code == 200
        data = res.json()["data"]
        assert "project" in data
        assert "summary" in data
        assert "habitat_zones" in data and len(data["habitat_zones"]["features"]) > 0
        assert "corridors" in data and len(data["corridors"]["features"]) > 0
        assert "priority_zones" in data and len(data["priority_zones"]["features"]) > 0
    test("Conservation GeoJSON Export Bundle (/api/v1/projects/{id}/export)", test_export)

    print("\n" + "=" * 70)
    print(f">> TEST SUITE SUMMARY: {passed_tests}/{total_tests} Tests Passed ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 70)
    assert passed_tests == total_tests, f"Failed {total_tests - passed_tests} tests"

if __name__ == "__main__":
    run_tests()
