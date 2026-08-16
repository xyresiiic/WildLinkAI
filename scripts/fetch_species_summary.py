import sqlite3

conn = sqlite3.connect('backend/wildlink.db')
cursor = conn.cursor()

cursor.execute("SELECT id, common_name, scientific_name, conservation_status FROM species")
species_list = cursor.fetchall()

print(f"| {'Species':<22} | {'Category':<22} | {'Conservation Status':<22} | {'Habitat Zones':<13} | {'Corridors':<10} | {'Priority Zones':<14} | {'What-If Net Gain':<20} |")
print("|" + "-"*24 + "|" + "-"*24 + "|" + "-"*24 + "|" + "-"*15 + "|" + "-"*12 + "|" + "-"*16 + "|" + "-"*22 + "|")

category_map = {
    "Bengal Tiger": "Apex Carnivore",
    "Indian Elephant": "Megaherbivore",
    "Indian Leopard": "Adaptable Carnivore",
    "Sloth Bear": "Omnivore",
    "Great Indian Bustard": "Grassland Specialist",
    "Gharial": "Riverine Reptile",
    "Snow Leopard": "Alpine Specialist"
}

for s_id, common_name, sci_name, status in species_list:
    cursor.execute("SELECT id FROM projects WHERE species_id = ? ORDER BY created_at DESC LIMIT 1", (s_id,))
    proj = cursor.fetchone()
    if not proj:
        continue
    p_id = proj[0]
    
    cursor.execute("SELECT COUNT(*) FROM habitat_zones WHERE project_id = ?", (p_id,))
    zones_cnt = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM corridors WHERE project_id = ?", (p_id,))
    corr_cnt = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM priority_zones WHERE project_id = ?", (p_id,))
    prio_cnt = cursor.fetchone()[0]
    
    cursor.execute("SELECT baseline_connectivity, simulated_connectivity, percentage_change FROM simulations WHERE project_id = ? ORDER BY created_at DESC LIMIT 1", (p_id,))
    sim = cursor.fetchone()
    if sim:
        sim_str = f"+{sim[1]-sim[0]:.2f} pts (+{sim[2]:.1f}%)"
    else:
        sim_str = "N/A"
        
    cat = category_map.get(common_name, "Wildlife")
    print(f"| {common_name:<22} | {cat:<22} | {status:<22} | {zones_cnt:<13} | {corr_cnt:<10} | {prio_cnt:<14} | {sim_str:<20} |")

conn.close()
