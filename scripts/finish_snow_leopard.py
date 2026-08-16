import time
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"
PROJECT_ID = "ee57cce8-9c59-4425-937f-ed5991565404"
JOB_ID = "c1490beb-0216-4705-854f-18c6cc1785fb"

print(f"Waiting for Snow Leopard Analysis Job {JOB_ID}...")
while True:
    res = requests.get(f"{BASE_URL}/analysis/jobs/{JOB_ID}").json()
    status = res.get("status")
    progress = res.get("progress", 0)
    print(f"Job status: {status} ({progress}%)")
    if status == "COMPLETED":
        break
    elif status == "FAILED":
        print(f"Job failed: {res.get('error')}")
        exit(1)
    time.sleep(5)

print("Job completed! Triggering What-If Simulation for Snow Leopard...")
sim_payload = {
    "project_id": PROJECT_ID,
    "name": "Snow Leopard High-Altitude Sanctuary Corridor",
    "intervention_type": "sanctuary_creation",
    "restoration_area_ha": 350.0,
    "parameters": {"protection_level": "strict"}
}
sim_res = requests.post(f"{BASE_URL}/simulations/run", json=sim_payload).json()
print("Simulation result:", sim_res)
