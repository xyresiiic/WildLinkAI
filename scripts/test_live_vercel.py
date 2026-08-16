import httpx
import json
import time

BASE = "https://wild-link-ai.vercel.app"

print("=== 1. Testing Species Endpoint ===")
r = httpx.get(f"{BASE}/api/v1/species", timeout=20)
print(f"Species status: {r.status_code}")
data = r.json().get("data", [])
print(f"Loaded {len(data)} species")
for sp in data[:3]:
    print(f"  - {sp.get('common_name')} ({sp.get('id')})")

print("\n=== 2. Testing Projects Endpoint ===")
r = httpx.get(f"{BASE}/api/v1/projects", timeout=20)
print(f"Projects status: {r.status_code}")
projects = r.json().get("data", [])
print(f"Loaded {len(projects)} projects")

for p in projects:
    p_id = p["id"]
    p_name = p.get("name")
    sp_name = p.get("species", {}).get("common_name") if p.get("species") else "Unknown"
    print(f"\n--- Project: {p_name} | Species: {sp_name} | ID: {p_id} ---")
    
    r_dash = httpx.get(f"{BASE}/api/v1/projects/{p_id}/dashboard", timeout=20)
    print(f"Dashboard ({r_dash.status_code}): {r_dash.text[:200]}")

    r_obs = httpx.get(f"{BASE}/api/v1/analysis/observations/{p_id}", timeout=20)
    obs_feat = len(r_obs.json().get("data", {}).get("features", [])) if r_obs.status_code == 200 else 0
    print(f"Observations ({r_obs.status_code}): {obs_feat} features")

    r_hab = httpx.get(f"{BASE}/api/v1/analysis/habitat/{p_id}", timeout=20)
    hab_feat = len(r_hab.json().get("data", {}).get("features", [])) if r_hab.status_code == 200 else 0
    print(f"Habitat Zones ({r_hab.status_code}): {hab_feat} features")

    r_corr = httpx.get(f"{BASE}/api/v1/analysis/corridors/{p_id}", timeout=20)
    corr_feat = len(r_corr.json().get("data", {}).get("features", [])) if r_corr.status_code == 200 else 0
    print(f"Corridors ({r_corr.status_code}): {corr_feat} features")

    r_prio = httpx.get(f"{BASE}/api/v1/analysis/priority/{p_id}", timeout=20)
    prio_feat = len(r_prio.json().get("data", {}).get("features", [])) if r_prio.status_code == 200 else 0
    print(f"Priority Zones ({r_prio.status_code}): {prio_feat} features")

if projects:
    test_p = projects[0]
    print(f"\n=== 4. Testing POST /api/v1/analysis/run for project {test_p['id']} ===")
    t0 = time.time()
    try:
        r_run = httpx.post(f"{BASE}/api/v1/analysis/run", json={"project_id": test_p["id"], "type": "full"}, timeout=35)
        print(f"Run status: {r_run.status_code} in {time.time()-t0:.2f}s")
        print(f"Run response: {r_run.text[:500]}")
    except Exception as e:
        print(f"Run failed in {time.time()-t0:.2f}s: {e}")
