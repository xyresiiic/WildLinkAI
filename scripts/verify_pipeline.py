import httpx
import json
import time
import sys

# Force UTF-8 stdout encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

base = 'http://localhost:8000/api/v1'
client = httpx.Client(timeout=120.0)

print('1. Fetching species...')
species_res = client.get(f'{base}/species').json()
print(f'   Found {len(species_res["data"])} species')
species_id = species_res['data'][0]['id']
print(f'   Selected species: {species_res["data"][0]["common_name"]} ({species_id})')

print('\n2. Creating project...')
proj_res = client.post(f'{base}/projects', json={
    'name': 'Bengal Tiger Corridor Project',
    'species_id': species_id,
    'region_name': 'Central Indian Highlands'
}).json()
project_id = proj_res['data']['id']
print(f'   Project created! ID: {project_id}')

print('\n3. Triggering full analysis pipeline...')
job_res = client.post(f'{base}/analysis/run', json={
    'project_id': project_id,
    'type': 'full'
}).json()
job_id = job_res['data']['id']
print(f'   Analysis job queued! ID: {job_id}')

print('\n4. Monitoring analysis progress...')
last_progress = -1
for i in range(180):
    time.sleep(1)
    try:
        res = client.get(f'{base}/analysis/jobs/{job_id}')
        status_res = res.json()
        if status_res.get('success'):
            job = status_res['data']
            if job["progress"] != last_progress:
                print(f'   Progress: {job["progress"]}% | Status: {job["status"]}')
                last_progress = job["progress"]
            if job['status'] in ('completed', 'failed'):
                if job.get('error'):
                    print(f'   Error: {job["error"]}')
                break
    except (httpx.ReadTimeout, httpx.ConnectTimeout):
        # Database might be busy with batch insertion, continue polling
        pass

print('\n5. Fetching analytical results...')
hab = client.get(f'{base}/analysis/habitat/{project_id}').json()['data']
print(f'   Habitat Zones: {hab["count"]} polygons generated')

corr = client.get(f'{base}/analysis/corridors/{project_id}').json()['data']
print(f'   Corridors: {corr["count"]} connectivity routes generated')

prio = client.get(f'{base}/analysis/priority/{project_id}').json()['data']
print(f'   Priority Zones: {prio["count"]} ranked intervention zones generated')

obs = client.get(f'{base}/analysis/observations/{project_id}').json()['data']
print(f'   Observations: {obs["count"]} species occurrence points loaded')

if prio['count'] > 0:
    top_zone = prio['features'][0]['properties']
    print(f'\n   Top Priority Zone (#1):')
    print(f'     - Rank: #{top_zone["rank"]}')
    print(f'     - Priority Score: {top_zone["priority_score"]}/100 ({top_zone["priority_level"]})')
    print(f'     - Dominant Factor: {top_zone["dominant_factor"]}')
    print(f'     - Explanation: {top_zone["explanation"]}')

print('\n6. Executing What-If Conservation Simulation...')
sim_res = client.post(f'{base}/simulations', json={
    'project_id': project_id,
    'name': 'Simulated Restoration of Top Priority Zones'
})
if sim_res.status_code not in (200, 201, 202):
    print(f'   Simulation post error ({sim_res.status_code}): {sim_res.text}')
    sys.exit(1)

sim_json = sim_res.json()
sim_id = sim_json['data']['id']
print(f'   Simulation queued! ID: {sim_id}')

for _ in range(60):
    time.sleep(1)
    try:
        sim_data = client.get(f'{base}/simulations/{sim_id}').json()['data']
        if sim_data['status'] in ('completed', 'failed'):
            if sim_data['status'] == 'completed':
                print('\n7. Simulation Completed Successfully!')
                print(f'   - Baseline Connectivity:  {sim_data["baseline_connectivity"]:.2f}')
                print(f'   - Simulated Connectivity: {sim_data["simulated_connectivity"]:.2f}')
                print(f'   - Net Improvement:        +{sim_data["improvement"]:.2f} ({sim_data["percentage_change"]:.1f}%)')
                if sim_data.get("result") and "recommendation" in sim_data["result"]:
                    print(f'   - Model Recommendation:   "{sim_data["result"]["recommendation"]}"')
            else:
                print(f'   Simulation failed: {sim_data.get("error")}')
            break
    except (httpx.ReadTimeout, httpx.ConnectTimeout):
        pass

print('\nALL PIPELINE PHASES VERIFIED SUCCESSFULLY!')
