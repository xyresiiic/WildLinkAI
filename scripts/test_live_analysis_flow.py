import httpx

BASE = "https://wild-link-ai.vercel.app"

# Test the exact endpoints - check what path the backend actually sees
endpoints = [
    ("GET", "/api/v1/projects"),
    ("GET", "/api/v1/species"),
    ("GET", "/api/v1/health"),
    ("GET", "/api/docs"),
    ("GET", "/api/v1/docs"),
    ("GET", "/"),
]

for method, path in endpoints:
    try:
        r = httpx.request(method, f"{BASE}{path}", timeout=15)
        print(f"{method} {path} -> {r.status_code} ({len(r.content)} bytes)")
    except Exception as e:
        print(f"{method} {path} -> ERROR: {e}")

# Now test the analysis run
print("\n--- Testing Analysis Run ---")
projs = httpx.get(f"{BASE}/api/v1/projects", timeout=15).json().get("data", [])
if projs:
    pid = projs[0]["id"]
    print(f"Project ID: {pid}")
    
    # This is the exact request the frontend makes
    r = httpx.post(f"{BASE}/api/v1/analysis/run", json={"project_id": pid, "type": "full"}, timeout=30)
    print(f"POST /api/v1/analysis/run -> {r.status_code}")
    print(f"Response: {r.text[:500]}")
