from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from enum import Enum
from datetime import datetime

class ResolutionStatus(str, Enum):
    ESCALATED = "Escalated to Human"
    RESOLVED = "Resolved by AI"
    REJECTED = "Rejected as Spam"
    ABANDONED = "Abandoned"

class InteractionCreate(BaseModel):
    callerName: Optional[str] = None
    callerNumber: Optional[str] = None
    organization: Optional[str] = None
    channel: Literal["Voice Call"] = "Voice Call"
    
    # Intent: max 2 words approx (approximate validation can be done, but we use strict typing here)
    intent: str = Field(..., max_length=50, description="Short intent classification (max 2 words)")
    sentiment: str
    urgency_score: int = Field(..., ge=1, le=10, description="Urgency score from 1-10")
    spam_confidence: int = Field(..., ge=0, le=100, description="Spam confidence 0-100%")
    resolution_status: ResolutionStatus
    summary: str
    action_items: Optional[List[str]] = None
    suggestedAction: Optional[str] = None
    transcript: str

class InteractionResponse(InteractionCreate):
    id: str = Field(..., description="The unique identifier of the interaction")
    created_at: datetime= Field(..., description="The timestamp of the call in the format \"YYYY-MM-DD HH:MM:SS\" on the region india.")
    
    # This config allows the use of generic Python types and proper serialization
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )
