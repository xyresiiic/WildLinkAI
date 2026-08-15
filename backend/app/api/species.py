"""
WildLink AI — Species API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database.connection import get_db
from app.models.models import Species
from app.schemas.schemas import SpeciesResponse, SpeciesCreate
from app.utils.helpers import success_response, error_response

router = APIRouter(prefix="/species", tags=["Species"])


@router.get("", response_model=None)
async def list_species(db: AsyncSession = Depends(get_db)):
    """Get all available species."""
    result = await db.execute(select(Species).order_by(Species.common_name))
    species_list = result.scalars().all()
    return success_response(
        data=[SpeciesResponse.model_validate(s).model_dump(mode="json") for s in species_list],
        message=f"Found {len(species_list)} species"
    )


@router.get("/{species_id}", response_model=None)
async def get_species(species_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific species by ID."""
    result = await db.execute(select(Species).where(Species.id == species_id))
    species = result.scalar_one_or_none()
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return success_response(data=SpeciesResponse.model_validate(species).model_dump(mode="json"))


@router.post("", response_model=None, status_code=201)
async def create_species(data: SpeciesCreate, db: AsyncSession = Depends(get_db)):
    """Create a new species entry."""
    species = Species(
        common_name=data.common_name,
        scientific_name=data.scientific_name,
        description=data.description,
        habitat_preferences=data.habitat_preferences,
        conservation_status=data.conservation_status,
    )
    db.add(species)
    await db.flush()
    await db.refresh(species)
    return success_response(
        data=SpeciesResponse.model_validate(species).model_dump(mode="json"),
        message="Species created"
    )
