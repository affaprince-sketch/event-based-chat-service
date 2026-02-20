# models.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageIn(BaseModel):
    user: str
    room: str = "default"
    text: str
    session_id: Optional[str] = None

class MessageOut(BaseModel):
    id: Optional[int] = None
    user: str
    room: str
    text: str
    role: str = "user"            # "user" or "ai"
    ts: datetime

class EventEnvelope(BaseModel):
    type: str
    data: dict

