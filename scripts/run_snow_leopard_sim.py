import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"
PROJECT_ID = "ee57cce8-9c59-4425-937f-ed5991565404"

print("Calculating priority zones for Snow Leopard...")
prio_res = requests.post(f"{BASE_URL}/priority/rank/{PROJECT_ID}").json()
print(f"Ranked {len(prio_res)} priority zones.")

print("Running What-If Simulation for Snow Leopard...")
sim_payload = {
    "project_id": PROJECT_ID,
    "name": "Alpine High-Pass Corridor Restoration",
    "intervention_type": "corridor_restoration",
    "restoration_area_ha": 300.0,
    "parameters": {"width_meters": 500}
}
res = requests.post(f"{BASE_URL}/simulations", json=sim_payload)
print("Simulation HTTP status:", res.status_code)
print("Simulation response text:", res.text)
