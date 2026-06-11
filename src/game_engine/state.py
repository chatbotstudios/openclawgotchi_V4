import sqlite3
import logging
import json
from datetime import datetime, timezone
from config import DB_PATH
from game_engine.models import AIPETState
from db.stats import get_level_progress

log = logging.getLogger(__name__)

def load_state() -> AIPETState:
    """Loads the AIPET state from the SQLite databases."""
    try:
        # Load XP/Level canonical info
        prog = get_level_progress()
        
        # Load vitals/meta from aipet_state
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM aipet_state WHERE id = 1").fetchone()
        conn.close()
        
        if not row:
            return AIPETState(level=prog["level"], xp=prog["xp"], title=prog["title"])
            
        data = dict(row)
        badges = json.loads(data.get("badges", "[]"))
        
        return AIPETState(
            level=prog["level"],
            xp=prog["xp"],
            title=prog["title"],
            hp=data.get("hp", 100.0),
            rp=data.get("rp", 0.0),
            missions_completed=data.get("missions_completed", 0),
            badges=badges,
            current_mood=data.get("current_mood", "neutral"),
            last_updated=data.get("last_updated", datetime.now(timezone.utc).isoformat())
        )
    except Exception as e:
        log.error(f"Failed to load AIPET state from SQLite: {e}")
        return AIPETState()

def save_state(state: AIPETState) -> bool:
    """Saves the non-XP AIPET state to the SQLite aipet_state table."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute('''
            UPDATE aipet_state 
            SET hp = ?, rp = ?, missions_completed = ?, badges = ?, current_mood = ?, last_updated = ?
            WHERE id = 1
        ''', (
            state.hp,
            state.rp,
            state.missions_completed,
            json.dumps(state.badges),
            state.current_mood,
            state.last_updated
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log.error(f"Failed to save AIPET state to SQLite: {e}")
        return False
