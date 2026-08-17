"""
Verify that the live Vercel deployment has deterministic project IDs and 
analysis works end-to-end.
"""
import httpx

BASE = "https://wild-link-ai.vercel.app"

# Expected deterministic project IDs (uuid5 with namespace a1b2c3d4-e5f6-7890-abcd-ef1234567890)
EXPECTED_TIGER_PROJECT_ID = "a1472e90-ac90-5458-9f10-022344599853"

print("=== WildLink AI Live Verification ===\n")

# 1. Projects
print("1. Fetching projects...")
r = httpx.get(f"{BASE}/api/v1/projects", timeout=20)
print(f"   Status: {r.status_code}")
projs = r.json().get("data", [])
print(f"   Projects count: {len(projs)}")
for p in projs:
    print(f"   - {p['id']}  {p['name']}")

# 2. Species
print("\n2. Fetching species...")
r = httpx.get(f"{BASE}/api/v1/species", timeout=15)
species = r.json().get("data", [])
print(f"   Species count: {len(species)}")
for s in species:
    print(f"   - {s['id']}  {s['common_name']}")

# 3. Run analysis on first project
if projs:
    pid = projs[0]["id"]
    print(f"\n3. Running analysis on '{projs[0]['name']}' (ID: {pid})...")
    r = httpx.post(f"{BASE}/api/v1/analysis/run", json={"project_id": pid, "type": "full"}, timeout=30)
    print(f"   Status: {r.status_code}")
    data = r.json()
    print(f"   Analysis status: {data.get('data', {}).get('status')}")
    print(f"   Progress: {data.get('data', {}).get('progress')}")
    
    # 4. Dashboard
    print(f"\n4. Dashboard for project {pid}...")
    r = httpx.get(f"{BASE}/api/v1/projects/{pid}/dashboard", timeout=15)
    dash = r.json().get("data", {})
    print(f"   Habitat Score: {dash.get('habitat_score')}")
    print(f"   Connectivity: {dash.get('connectivity_score')}")
    print(f"   Corridors: {dash.get('total_corridors')}")
    print(f"   Priority Zones: {dash.get('total_priority_zones')}")
    
    # 5. Test with a STALE project ID (simulates old browser hash)
    stale_id = "9affb1fb-516e-440c-961e-83dae58cc15d"
    print(f"\n5. Testing stale project ID '{stale_id}'...")
    r = httpx.post(f"{BASE}/api/v1/analysis/run", json={"project_id": stale_id, "type": "full"}, timeout=15)
    print(f"   Status: {r.status_code} (expected 404)")
    
    # 6. Test with old project GET (simulates checkUrlHash)
    r = httpx.get(f"{BASE}/api/v1/projects/{stale_id}", timeout=15)
    print(f"   GET /projects/{stale_id}: {r.status_code} (expected 404)")

print("\n=== Verification Complete ===")
