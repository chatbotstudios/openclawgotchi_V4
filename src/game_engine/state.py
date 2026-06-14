import sqlite3
import logging
import json
from datetime import datetime, timezone
from typing import Optional

from config import DB_PATH
from game_engine.models import AIPETState, AgentStatus
from db.stats import get_level_progress
from game_engine.events import events

log = logging.getLogger(__name__)

class StateManager:
    """
    Singleton Manager for AIPET state.
    Provides RAM caching to prevent SD-card I/O spam and emits events on state changes.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance._cached_state = None
        return cls._instance

    def load_state(self, force_reload: bool = False) -> AIPETState:
        """Loads the AIPET state, preferring the RAM cache unless forced."""
        if self._cached_state and not force_reload:
            return self._cached_state
            
        try:
            prog = get_level_progress()
            
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM aipet_state WHERE id = 1").fetchone()
            conn.close()
            
            if not row:
                self._cached_state = AIPETState(level=prog["level"], xp=prog["xp"], title=prog["title"])
                return self._cached_state
                
            data = dict(row)
            badges = json.loads(data.get("badges", "[]"))
            
            # Note: status is not persisted to DB yet (it's volatile), defaults to AWAKE
            self._cached_state = AIPETState(
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
            return self._cached_state
        except Exception as e:
            log.error(f"Failed to load AIPET state from SQLite: {e}")
            return AIPETState()

    def save_state(self, state: Optional[AIPETState] = None) -> bool:
        """Saves the state to SQLite and updates the cache."""
        if state is None:
            if self._cached_state is None:
                return False
            state = self._cached_state
        else:
            self._cached_state = state

        try:
            state.last_updated = datetime.now(timezone.utc).isoformat()
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
            
            # Emit state changed event
            events.emit("state_changed", state)
            return True
        except Exception as e:
            log.error(f"Failed to save AIPET state to SQLite: {e}")
            return False

    def change_status(self, new_status: AgentStatus):
        state = self.load_state()
        if state.status != new_status:
            old_status = state.status
            state.status = new_status
            self.save_state(state)
            events.emit("status_changed", {"old": old_status, "new": new_status})
            log.info(f"Agent status changed: {old_status} -> {new_status}")

    def enter_dream_state(self):
        self.change_status(AgentStatus.DREAMING)

    def wake_up(self):
        self.change_status(AgentStatus.AWAKE)

# Global singleton
state_manager = StateManager()

# Legacy wrappers for backward compatibility
def load_state() -> AIPETState:
    return state_manager.load_state()

def save_state(state: AIPETState) -> bool:
    return state_manager.save_state(state)
