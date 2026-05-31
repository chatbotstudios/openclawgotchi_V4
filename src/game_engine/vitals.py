import sqlite3
import logging
from datetime import datetime, timezone
from config import DB_PATH
from src.game_engine.state import load_state, save_state

log = logging.getLogger(__name__)

def xp_to_reach_level(n: int) -> int:
    """Formula for progressive leveling scaling."""
    if n <= 10:
        return n * 100
    else:
        return 1000 + (n - 10) * 1000

def calculate_hp(cpu: float, mem: float, uptime_hours: float, battery: float = 100.0) -> float:
    """Calculate the HP of the AIPET based on hardware vitals."""
    hp = (uptime_hours * 1.5) + ((100 - cpu) * 0.4) + ((100 - mem) * 0.3) + (battery * 0.2)
    return max(0.0, min(100.0, hp))

def add_xp(amount: int, source: str = "mission", event=None) -> int:
    """Awards XP to the AIPET, checks for level up, and logs to SQLite."""
    state = load_state()
    state.xp += amount
    
    # Update timestamp
    state.last_updated = datetime.now(timezone.utc).isoformat()
    
    # Check for level up
    leveled_up = False
    next_level_xp = xp_to_reach_level(state.level + 1)
    
    while state.xp >= next_level_xp and state.level < 100:
        state.level += 1
        leveled_up = True
        log.info(f"🎉 AIPET LEVELED UP to Level {state.level}!")
        
        if event is not None:
            event.messages.append(f"🎉 **LEVEL UP!** Gotchi reached Level {state.level}! 🚀")
            
        try:
            from hardware.display import show_face
            show_face("excited", f"SAY:Level {state.level}! | STATUS: LEVEL UP", full_refresh=False)
        except Exception as e:
            log.warning(f"Failed to flash E-paper on level up: {e}")
            
        next_level_xp = xp_to_reach_level(state.level + 1)
        
    save_state(state)
    
    # Log to SQLite
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute('''
            INSERT INTO aipet_vitals_log (timestamp, xp, hp, rp, level, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (state.last_updated, state.xp, state.hp, state.rp, state.level, source))
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Failed to log vitals to database: {e}")
        
    return state.xp
