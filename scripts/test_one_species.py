import sys
import os
import asyncio
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import Species, Project
from app.engines.habitat_engine import HabitatEngine
from app.engines.fragmentation_engine import FragmentationEngine
from app.engines.resistance_engine import ResistanceEngine
from app.engines.connectivity_engine import ConnectivityEngine
from app.engines.priority_engine import PriorityEngine

async def test_species(name="Snow Leopard"):
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Species).where(Species.common_name == name))
        sp = res.scalar_one_or_none()
        proj_res = await db.execute(select(Project).where(Project.species_id == sp.id).limit(1))
        proj = proj_res.scalar_one_or_none()

        print(f"Testing {name} (Project {proj.id}, Region: {proj.region_name})")

        t0 = time.time()
        he = HabitatEngine(proj.id, db)
        await he.run()
        await db.commit()
        print(f"1. Habitat Engine: {time.time() - t0:.3f}s")

        t0 = time.time()
        fe = FragmentationEngine(proj.id, db)
        await fe.run()
        await db.commit()
        print(f"2. Fragmentation Engine: {time.time() - t0:.3f}s")

        t0 = time.time()
        re = ResistanceEngine(proj.id, db)
        await re.run()
        await db.commit()
        print(f"3. Resistance Engine: {time.time() - t0:.3f}s")

        t0 = time.time()
        ce = ConnectivityEngine(proj.id, db)
        await ce.run()
        await db.commit()
        print(f"4. Connectivity Engine: {time.time() - t0:.3f}s")

        t0 = time.time()
        pe = PriorityEngine(proj.id, db)
        await pe.run()
        await db.commit()
        print(f"5. Priority Engine: {time.time() - t0:.3f}s")

if __name__ == "__main__":
    asyncio.run(test_species(sys.argv[1] if len(sys.argv) > 1 else "Snow Leopard"))
