from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone

def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

class AIPETState(BaseModel):
    """
    AIPET runtime state — persisted to templates/AIPET_STATE.json.

    NOTE: `level`, `xp`, and `title` are write-through mirrors of the canonical
    gotchi_stats SQLite table (db/stats.py). They are kept here for fast access
    by hardware/display code without requiring a DB query, but db/stats.py is
    always the authoritative source of truth for XP and level.
    """
    # ── Game stats (mirrors of db/stats.py canonical store) ──
    level: int = 1
    xp: int = 0
    title: str = "Newborn"          # synced from db.stats.LEVEL_TITLES on each XP write

    # ── Hardware vitals ──
    hp: float = 100.0
    rp: float = 0.0

    # ── Meta ──
    last_updated: str = Field(default_factory=_now_utc)
    missions_completed: int = 0
    badges: List[str] = Field(default_factory=list)
    current_mood: str = "neutral"
