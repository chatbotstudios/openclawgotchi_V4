import sqlite3
import logging
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional
from config import DB_PATH, WORKSPACE_DIR, MISSIONS_DIR
from src.game_engine.vitals import add_xp
from src.game_engine.state import load_state, save_state

log = logging.getLogger(__name__)

MISSIONS_FILE = MISSIONS_DIR / "progressive.json"

def load_progressive_missions():
    """Injects progressive missions into the database from JSON if they don't exist."""
    if not MISSIONS_FILE.exists():
        log.warning(f"Missions file not found: {MISSIONS_FILE}")
        return

    try:
        with open(MISSIONS_FILE, "r") as f:
            missions_data = json.load(f)

        conn = sqlite3.connect(str(DB_PATH))
        for m in missions_data:
            # Check if exists
            row = conn.execute("SELECT id FROM aipet_missions WHERE name = ?", (m["name"],)).fetchone()
            if not row:
                # Active if it ends with "v1" or is a single-tier mission (base_name is null/empty or equals name)
                is_progressive = bool(m.get("base_name") and m["base_name"] != m["name"])
                initial_status = "active" if (not is_progressive or m["name"].endswith("v1")) else "pending"
                
                conn.execute('''
                    INSERT INTO aipet_missions (name, base_name, category, xp_reward, target, progress, status, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (m["name"], m["base_name"], m["category"], m["xp_reward"], m["target"], 0, initial_status, m.get("source", "auto")))
        conn.commit()
        conn.close()
        log.info("Progressive missions loaded.")
    except Exception as e:
        log.error(f"Failed to load progressive missions: {e}")

def get_missions(status_filter: Optional[str] = None) -> List[Dict]:
    """Retrieves missions from the database, optionally filtered by status."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        if status_filter:
            cursor = conn.execute("SELECT * FROM aipet_missions WHERE status = ? ORDER BY id ASC", (status_filter,))
        else:
            cursor = conn.execute("SELECT * FROM aipet_missions ORDER BY id ASC")
        missions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return missions
    except Exception as e:
        log.error(f"Failed to retrieve missions: {e}")
        return []

def complete_mission(name: str, event=None) -> bool:
    """Marks a mission as completed, awards XP, and updates state. Unlocks the next tier if available."""
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
            SET status = 'completed', completed_at = ?, progress = target
            WHERE id = ?
        ''', (now_str, mission["id"]))
        
        # Unlock next tier (e.g. if completed v1, unlock v2)
        if mission["base_name"]:
            # Find the next pending tier for this base_name
            next_tier = conn.execute('''
                SELECT id, name FROM aipet_missions 
                WHERE base_name = ? AND status = 'pending' 
                ORDER BY id ASC LIMIT 1
            ''', (mission["base_name"],)).fetchone()
            
            if next_tier:
                conn.execute("UPDATE aipet_missions SET status = 'active' WHERE id = ?", (next_tier["id"],))
                log.info(f"🔓 Unlocked next mission tier: {next_tier['name']}")

        conn.commit()
        conn.close()
        
        # Award XP and update state
        add_xp(mission["xp_reward"], source=f"mission:{mission['name']}", event=event)
        
        state = load_state()
        state.missions_completed += 1
        save_state(state)
        
        log.info(f"✅ Mission Completed: {mission['name']} (+{mission['xp_reward']} XP)")
        
        if event is not None:
            event.messages.append(f"🎉 You completed mission **{mission['name']}**! +{mission['xp_reward']} XP 🚀")
            
        try:
            from hardware.display import show_face
            show_face("excited", f"SAY:Mission Done! | STATUS: +{mission['xp_reward']} XP", full_refresh=False)
        except Exception as e:
            log.warning(f"Failed to flash E-paper on mission complete: {e}")
            
        # Write to Daily Memory Log
        try:
            from memory.flush import write_to_daily_log
            write_to_daily_log(f"🏆 Completed Mission: **{mission['name']}** (+{mission['xp_reward']} XP)")
        except Exception as e:
            log.warning(f"Failed to log mission to daily log: {e}")

        # Broadcast to Discord #heartbeats
        try:
            from core.missions.notifications import _send_discord_webhook
            import threading
            content = f"🏆 **Mission Complete!**\n> **{mission['name']}**\n*+{mission['xp_reward']} XP gained!*"
            t = threading.Thread(target=_send_discord_webhook, args=({"content": content},))
            t.daemon = True
            t.start()
        except Exception as e:
            log.warning(f"Failed to trigger Discord heartbeat mission webhook: {e}")
            
        return True
    except Exception as e:
        log.error(f"Failed to complete mission: {e}")
        return False

def increment_mission_progress(base_name: str, amount: int = 1, event=None):
    """Increments progress for the active tier of a specific mission base_name."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        
        # Find the currently active tier for this base_name
        row = conn.execute('''
            SELECT * FROM aipet_missions 
            WHERE base_name = ? AND status = 'active'
            ORDER BY id ASC LIMIT 1
        ''', (base_name,)).fetchone()
        
        if not row:
            conn.close()
            return # No active mission for this base_name
            
        mission = dict(row)
        new_progress = min(mission["progress"] + amount, mission["target"])
        
        conn.execute("UPDATE aipet_missions SET progress = ? WHERE id = ?", (new_progress, mission["id"]))
        conn.commit()
        conn.close()
        
        log.debug(f"Mission '{mission['name']}' progress: {new_progress}/{mission['target']}")
        
        if new_progress >= mission["target"]:
            complete_mission(mission["name"], event=event)
            
    except Exception as e:
        log.error(f"Failed to increment mission progress: {e}")

def _generate_dream_async():
    import asyncio
    from core.router import get_router
    
    async def _run():
        router = get_router()
        prompt = (
            "You are an AI hacker pet currently in a DREAM STATE. "
            "1. Write a 2-sentence surreal, cyberpunk dream about your past experiences or network captures. "
            "2. While dreaming, use the `aipet_generate_bounty` tool to spontaneously invent a new procedural mission for yourself based on the dream! Make the mission target something fun or tactical (e.g. 'Sniff 10 packets', 'Find an Apple device')."
        )
        try:
            response, _ = await router.call(prompt, history=[])
            log.info(f"💭 Dream generated: {response}")
            
            # Save dream to daily log
            from memory.flush import write_to_daily_log
            write_to_daily_log(f"💭 **Dream Sequence:** {response}")
            
        except Exception as e:
            log.error(f"Failed to generate dream via LLM: {e}")
            
    # Run the async function in a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_run())
    loop.close()

def trigger_dream():
    """Manually invokes a dream session, awarding XP, altering mood, and generating procedural content."""
    add_xp(60, source="dream_session")
    increment_mission_progress("Synthetic Strategist", 1)
    
    state = load_state()
    state.current_mood = "dreaming"
    save_state(state)
    
    log.info("💭 AIPET entered Dream State. Initializing procedural dream generation...")
    
    import threading
    t = threading.Thread(target=_generate_dream_async, daemon=True)
    t.start()

# Initialize progressive missions on module load
load_progressive_missions()
