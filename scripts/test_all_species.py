import httpx
import time

BASE = "https://wild-link-ai.vercel.app"
print("Fetching all projects from Vercel...")
r = httpx.get(f"{BASE}/api/v1/projects", timeout=15)
projects = r.json().get("data", [])
print(f"Found {len(projects)} projects.")

for p in projects:
    p_id = p["id"]
    p_name = p.get("name", "Unknown")
    t0 = time.time()
    res = httpx.post(f"{BASE}/api/v1/analysis/run", json={"project_id": p_id, "type": "full"}, timeout=20)
    elapsed = time.time() - t0
    print(f"[{res.status_code}] {p_name} analyzed in {elapsed:.2f}s")
    
    # Query dashboard to confirm
    dash = httpx.get(f"{BASE}/api/v1/projects/{p_id}/dashboard", timeout=15).json().get("data", {})
    hab = httpx.get(f"{BASE}/api/v1/projects/{p_id}/habitat-zones", timeout=15).json().get("data", {}).get("features", [])
    corr = httpx.get(f"{BASE}/api/v1/projects/{p_id}/corridors", timeout=15).json().get("data", {}).get("features", [])
    prio = httpx.get(f"{BASE}/api/v1/projects/{p_id}/priority-zones", timeout=15).json().get("data", {}).get("features", [])
    print(f"     => Hab Score: {dash.get('habitat_score')} | Conn Score: {dash.get('connectivity_score')} | Zones: {len(hab)} | Corridors: {len(corr)} | Priorities: {len(prio)}")
