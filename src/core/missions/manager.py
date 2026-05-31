import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Optional

from config import DB_PATH, WORKSPACE_DIR
from core.missions.models import Mission

log = logging.getLogger(__name__)

def init_missions_table():
    """Initialize missions table if not exists."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('''
        CREATE TABLE IF NOT EXISTS missions (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            category TEXT,
            tier TEXT,
            status TEXT DEFAULT 'available',
            progress INTEGER DEFAULT 0,
            target INTEGER,
            reward_xp INTEGER,
            trigger_event TEXT,
            actor TEXT DEFAULT 'any'
        )
    ''')
    
    # Auto-migration for existing v3.0.3 databases
    try:
        conn.execute("SELECT actor FROM missions LIMIT 1")
    except sqlite3.OperationalError:
        try:
            log.info("Auto-migrating missions table: adding 'actor' column...")
            conn.execute("ALTER TABLE missions ADD COLUMN actor TEXT DEFAULT 'any'")
        except Exception as e:
            log.warning(f"Failed to auto-migrate 'actor' column: {e}")
            
    conn.commit()
    conn.close()

def load_default_missions():
    """Load default missions from JSON into the database."""
    default_path = WORKSPACE_DIR / "missions" / "default.json"
    if not default_path.exists():
        return

    try:
        with open(default_path, "r") as f:
            missions_data = json.load(f)
            
        conn = sqlite3.connect(str(DB_PATH))
        for m in missions_data:
            conn.execute('''
                INSERT OR IGNORE INTO missions 
                (id, title, description, category, tier, target, reward_xp, trigger_event, actor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                m["id"], m["title"], m["description"], 
                m["category"], m["tier"], m["target"], 
                m["reward_xp"], m.get("trigger_event", ""), m.get("actor", "any")
            ))
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Failed to load default missions: {e}")

def get_missions(status: Optional[str] = None) -> List[Mission]:
    """Get missions optionally filtered by status."""
    conn = sqlite3.connect(str(DB_PATH))
    if status:
        cursor = conn.execute("SELECT * FROM missions WHERE status = ?", (status,))
    else:
        cursor = conn.execute("SELECT * FROM missions")
        
    missions = [Mission.from_row(row) for row in cursor.fetchall()]
    conn.close()
    return missions

def get_mission(mission_id: str) -> Optional[Mission]:
    """Get a single mission by ID."""
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute("SELECT * FROM missions WHERE id = ?", (mission_id,)).fetchone()
    conn.close()
    if row:
        return Mission.from_row(row)
    return None

def update_mission_status(mission_id: str, new_status: str):
    """Change mission status."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("UPDATE missions SET status = ? WHERE id = ?", (new_status, mission_id))
    conn.commit()
    conn.close()
    
    m = get_mission(mission_id)
    if m:
        from core.missions.notifications import notify_discord_mission
        notify_discord_mission(m, new_status)

def increment_mission_progress(mission_id: str, amount: int = 1) -> Mission:
    """Increment progress for a mission."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("UPDATE missions SET progress = progress + ? WHERE id = ?", (amount, mission_id))
    conn.commit()
    conn.close()
    
    m = get_mission(mission_id)
    if m and m.progress >= m.target and m.status == 'active':
        from core.missions.rewards import dispense_mission_reward
        update_mission_status(mission_id, 'completed')
        dispense_mission_reward(m)
        m.status = 'completed'
    return m

# Initialize on import
try:
    init_missions_table()
    load_default_missions()
except Exception as e:
    log.warning(f"Failed to init missions: {e}")
