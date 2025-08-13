from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum

# enum for type validation

class MessageType(str, Enum):
    human = "human"
    ai = "ai"


class chathistory(BaseModel):
    sessionId: str = Field(min_length=2, description="session id for the chatting")
    content: str
    is_bookmark:bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at:Optional[datetime] = None 
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "sessionId": "64f2a9c2f4a4b8a2f8d3d12a",
                "content": "This is about chat",
                "is_bookmark":"true",
                "created_at": "2025-07-17T12:34:56Z",
                "updated_at": None
            }
        }
    
    
    
    
    
    
    
    
    
    
 