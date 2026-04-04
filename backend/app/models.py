from datetime import datetime, timezone
from app.schemas import InteractionCreate

def create_interaction_document(interaction: InteractionCreate) -> dict:
    """
    Converts a Pydantic InteractionsCreate model into a document dictionary 
    suitable for MongoDB insertion, adding necessary metadata.
    """
    doc = interaction.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    return doc

def format_interaction_response(doc: dict) -> dict:
    """
    Formats a MongoDB document for output, extracting _id to id string format.
    """
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        # We can optionally drop _id or just let Pydantic model ignore it 
        # since response model maps id properly
    return doc
