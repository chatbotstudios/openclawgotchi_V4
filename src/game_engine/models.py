from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone

def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

class AIPETState(BaseModel):
    level: int = 1
    xp: int = 0
    hp: float = 100.0
    rp: float = 0.0
    last_updated: str = Field(default_factory=_now_utc)
    missions_completed: int = 0
    badges: List[str] = Field(default_factory=list)
    current_mood: str = "neutral"
