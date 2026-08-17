import httpx

BASE = "https://wild-link-ai.vercel.app"
projs = httpx.get(f"{BASE}/api/v1/projects", timeout=15).json().get("data", [])
print(f"Loaded {len(projs)} projects from {BASE}\n")

for p in projs:
    pid = p["id"]
    name = p["name"]
    hab_res = httpx.get(f"{BASE}/api/v1/analysis/habitat/{pid}", timeout=15).json()
    corr_res = httpx.get(f"{BASE}/api/v1/analysis/corridors/{pid}", timeout=15).json()
    prio_res = httpx.get(f"{BASE}/api/v1/analysis/priority/{pid}", timeout=15).json()
    obs_res = httpx.get(f"{BASE}/api/v1/analysis/observations/{pid}", timeout=15).json()
    dash = httpx.get(f"{BASE}/api/v1/projects/{pid}/dashboard", timeout=15).json().get("data", {})
    
    n_hab = len(hab_res.get("data", {}).get("features", []))
    n_corr = len(corr_res.get("data", {}).get("features", []))
    n_prio = len(prio_res.get("data", {}).get("features", []))
    n_obs = len(obs_res.get("data", {}).get("features", []))
    
    print(f"[{name}]")
    print(f"  - Habitat Score: {dash.get('habitat_score')}% ({n_hab} grid cells)")
    print(f"  - Connectivity Score: {dash.get('connectivity_score')}% ({n_corr} corridors)")
    print(f"  - Priority Zones: {n_prio} zones ranked (Critical: {dash.get('critical_zones')})")
    print(f"  - Field Observations: {n_obs} survey points\n")
