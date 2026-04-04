from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.schemas import InteractionCreate, InteractionResponse
from app.services import interaction_service

router = APIRouter(prefix="/interactions", tags=["Interactions"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_interaction(interaction: InteractionCreate):
    """
    Creates a new call interaction analytics record.
    Accepts structured interaction data and stores it in the database.
    """
    interaction_id = await interaction_service.create_interaction(interaction)
    return {"id": interaction_id, "message": "Interaction created successfully"}

@router.get("/", response_model=List[InteractionResponse])
async def fetch_interactions(
    intent: Optional[str] = Query(None, description="Filter by exact intent string"),
    urgency_min: Optional[int] = Query(None, description="Minimum urgency score bounds"),
    urgency_max: Optional[int] = Query(None, description="Maximum urgency score bounds"),
    spam_confidence: Optional[int] = Query(None, description="Exact spam confidence to filter on")
):
    """
    Returns a list of interactions. Filters can be provided via query parameters.
    """
    filters = {
        "intent": intent,
        "urgency_score_min": urgency_min,
        "urgency_score_max": urgency_max,
        "spam_confidence": spam_confidence
    }
    interactions = await interaction_service.get_interactions(filters)
    return interactions

@router.get("/{interaction_id}", response_model=InteractionResponse)
async def fetch_interaction_by_id(interaction_id: str):
    """
    Fetches a specific interaction record by its ID.
    Raises a 404 error if it does not exist.
    """
    interaction = await interaction_service.get_interaction_by_id(interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction

@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_interaction(interaction_id: str):
    """
    Deletes a specific interaction record by its ID.
    Raises a 404 error if it does not exist.
    """
    success = await interaction_service.delete_interaction(interaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction not found or invalid ID format")
    return None
