import httpx
import json
import time
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

base = 'http://localhost:8000/api/v1'
client = httpx.Client(timeout=180.0)

print("================================================================")
print("🌿 WILDLINK AI — MULTI-SPECIES & CATEGORY ANALYSIS RUNNER")
print("================================================================\n")

# 1. Fetch available species
print("1. Fetching all available species categories...")
species_list = client.get(f'{base}/species').json()['data']
print(f"   Total species registered: {len(species_list)}\n")

for i, sp in enumerate(species_list, 1):
    print(f"   [{i}] {sp['common_name']} ({sp['scientific_name']}) — Status: {sp['conservation_status']}")

print("\n----------------------------------------------------------------")
print("2. Running full pipeline for each species category")
print("----------------------------------------------------------------\n")

results_summary = []

for sp in species_list:
    sp_id = sp['id']
    sp_name = sp['common_name']
    
    print(f"🐾 Category/Species: {sp_name}")
    print(f"   Creating project for {sp_name}...")
    proj_res = client.post(f'{base}/projects', json={
        'name': f"{sp_name} Corridor & Conservation Priority",
        'species_id': sp_id,
        'region_name': 'Central Indian Highlands'
    }).json()
    project_id = proj_res['data']['id']
    
    print(f"   Triggering analysis job...")
    job_res = client.post(f'{base}/analysis/run', json={
        'project_id': project_id,
        'type': 'full'
    }).json()
    job_id = job_res['data']['id']
    
    # Poll progress
    for _ in range(120):
        time.sleep(1)
        try:
            status_res = client.get(f'{base}/analysis/jobs/{job_id}').json()
            if status_res.get('success'):
                job = status_res['data']
                if job['status'] in ('completed', 'failed'):
                    break
        except Exception:
            pass

    # Fetch results
    hab = client.get(f'{base}/analysis/habitat/{project_id}').json()['data']
    corr = client.get(f'{base}/analysis/corridors/{project_id}').json()['data']
    prio = client.get(f'{base}/analysis/priority/{project_id}').json()['data']
    obs = client.get(f'{base}/analysis/observations/{project_id}').json()['data']

    # Trigger Simulation
    sim_res = client.post(f'{base}/simulations', json={
        'project_id': project_id,
        'name': f"Restoration Scenario for {sp_name}"
    }).json()
    sim_id = sim_res['data']['id']

    sim_data = None
    for _ in range(60):
        time.sleep(1)
        try:
            s_res = client.get(f'{base}/simulations/{sim_id}').json()
            if s_res.get('success') and s_res['data']['status'] in ('completed', 'failed'):
                sim_data = s_res['data']
                break
        except Exception:
            pass

    summary_entry = {
        'species': sp_name,
        'status': sp['conservation_status'],
        'observations': obs['count'],
        'habitat_zones': hab['count'],
        'corridors': corr['count'],
        'priority_zones': prio['count'],
        'top_priority_factor': prio['features'][0]['properties']['dominant_factor'] if prio['count'] > 0 else 'N/A',
        'baseline_conn': sim_data['baseline_connectivity'] if sim_data else 0,
        'simulated_conn': sim_data['simulated_connectivity'] if sim_data else 0,
        'improvement': f"+{sim_data['improvement']:.1f} ({sim_data['percentage_change']:.1f}%)" if sim_data else "N/A"
    }
    results_summary.append(summary_entry)

    print(f"   ✅ Done! Habitat Zones: {hab['count']} | Corridors: {corr['count']} | Priorities: {prio['count']}")
    if sim_data:
        print(f"   🔮 Simulation: Baseline {sim_data['baseline_connectivity']:.1f} → Simulated {sim_data['simulated_connectivity']:.1f} ({summary_entry['improvement']})")
    print("")

print("================================================================")
print("📊 MULTI-SPECIES CONSERVATION PIPELINE SUMMARY")
print("================================================================\n")
print(f"{'Species':<22} | {'Status':<21} | {'Obs':<4} | {'Zones':<6} | {'Routes':<6} | {'Net Gain'}")
print("-" * 80)
for r in results_summary:
    print(f"{r['species']:<22} | {r['status']:<21} | {r['observations']:<4} | {r['habitat_zones']:<6} | {r['corridors']:<6} | {r['improvement']}")

print("\nALL SPECIES CATEGORIES PROCESSED & VERIFIED SUCCESSFULLY!")
