import sqlite3
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from config import DB_PATH
from src.game_engine.vitals import add_xp
from src.game_engine.state import load_state, save_state

log = logging.getLogger(__name__)

STARTER_MISSIONS = [
    {
        "name": "Cortex Calibration",
        "category": "Cortex",
        "xp_reward": 150,
        "source": "auto"
    },
    {
        "name": "Radio Collector",
        "category": "Radio",
        "xp_reward": 80,
        "source": "auto"
    },
    {
        "name": "Uptime Resilience",
        "category": "Uptime",
        "xp_reward": 120,
        "source": "auto"
    },
    {
        "name": "Social Sync",
        "category": "Social",
        "xp_reward": 200,
        "source": "auto"
    },
    {
        "name": "Dream Session",
        "category": "Cortex",
        "xp_reward": 60,
        "source": "auto"
    }
]

def load_starter_missions():
    """Injects starter missions into the database if they don't exist."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        for m in STARTER_MISSIONS:
            # Check if exists
            row = conn.execute("SELECT id FROM aipet_missions WHERE name = ?", (m["name"],)).fetchone()
            if not row:
                conn.execute('''
                    INSERT INTO aipet_missions (name, category, xp_reward, status, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (m["name"], m["category"], m["xp_reward"], "active", m["source"]))
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Failed to load starter missions: {e}")

def get_missions(status_filter: Optional[str] = None) -> List[Dict]:
    """Retrieves missions from the database, optionally filtered by status."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        if status_filter:
            cursor = conn.execute("SELECT * FROM aipet_missions WHERE status = ?", (status_filter,))
        else:
            cursor = conn.execute("SELECT * FROM aipet_missions")
        missions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return missions
    except Exception as e:
        log.error(f"Failed to retrieve missions: {e}")
        return []

def complete_mission(name: str) -> bool:
    """Marks a mission as completed, awards XP, and updates state."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM aipet_missions WHERE name = ? AND status != 'completed'", (name,)).fetchone()
        
        if not row:
            conn.close()
            return False
            
        mission = dict(row)
        now_str = datetime.now(timezone.utc).isoformat()
        
        # Update mission status
        conn.execute('''
            UPDATE aipet_missions 
            SET status = 'completed', completed_at = ?
            WHERE id = ?
        ''', (now_str, mission["id"]))
        conn.commit()
        conn.close()
        
        # Award XP and update state
        add_xp(mission["xp_reward"], source=f"mission:{mission['name']}")
        
        state = load_state()
        state.missions_completed += 1
        save_state(state)
        
        log.info(f"✅ Mission Completed: {mission['name']} (+{mission['xp_reward']} XP)")
        return True
    except Exception as e:
        log.error(f"Failed to complete mission: {e}")
        return False

def trigger_dream():
    """Manually invokes a dream session, awarding XP and altering mood."""
    add_xp(60, source="dream_session")
    
    state = load_state()
    state.current_mood = "dreaming"
    save_state(state)
    
    log.info("💭 AIPET entered Dream State.")

# Initialize starter missions on module load
load_starter_missions()
