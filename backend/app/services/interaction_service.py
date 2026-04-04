from bson import ObjectId
from typing import List, Optional, Dict, Any
from app.database import get_interactions_collection
from app.schemas import InteractionCreate
from app.models import create_interaction_document, format_interaction_response

async def create_interaction(data: InteractionCreate) -> str:
    """
    Takes validated interaction data, saves it to the database, 
    and returns its newly generated ID.
    """
    collection = get_interactions_collection()
    doc = create_interaction_document(data)
    result = await collection.insert_one(doc)
    return str(result.inserted_id)

async def get_interactions(filters: Dict[str, Any]) -> List[dict]:
    """
    Retrieves interactions based on provided filters.
    """
    collection = get_interactions_collection()
    
    query = {}
    
    if "intent" in filters and filters["intent"]:
        query["intent"] = filters["intent"]
    
    if "urgency_score_min" in filters or "urgency_score_max" in filters:
        query["urgency_score"] = {}
        if filters.get("urgency_score_min") is not None:
            query["urgency_score"]["$gte"] = filters["urgency_score_min"]
        if filters.get("urgency_score_max") is not None:
            query["urgency_score"]["$lte"] = filters["urgency_score_max"]
        
        # Cleanup if empty
        if not query["urgency_score"]:
            del query["urgency_score"]
            
    if "spam_confidence" in filters and filters["spam_confidence"] is not None:
        query["spam_confidence"] = filters["spam_confidence"]

    cursor = collection.find(query).sort("created_at", -1)
    
    # In production, add pagination limits here (e.g. limit(100))
    interactions = await cursor.to_list(length=100)
    
    return [format_interaction_response(doc) for doc in interactions]

async def get_interaction_by_id(interaction_id: str) -> Optional[dict]:
    """
    Retrieves a single interaction by its string ID.
    Returns None if not found or if the ID is invalid.
    """
    collection = get_interactions_collection()
    try:
        obj_id = ObjectId(interaction_id)
    except Exception:
        return None
        
    doc = await collection.find_one({"_id": obj_id})
    if doc:
        return format_interaction_response(doc)
    return None

async def delete_interaction(interaction_id: str) -> bool:
    """
    Deletes an interaction by ID. Returns True if successfully deleted.
    """
    collection = get_interactions_collection()
    try:
        obj_id = ObjectId(interaction_id)
    except Exception:
        return False
        
    result = await collection.delete_one({"_id": obj_id})
    return result.deleted_count > 0
