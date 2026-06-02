import asyncio
import time
import re
import random
import logging
from rich.live import Live
from rich.console import Console

from cli.dashboard.fetchers import (
    fetch_system_stats,
    fetch_gotchi_stats,
    fetch_pwn_status,
    fetch_recent_logs,
    fetch_missions_status
)
from cli.dashboard.layout import (
    generate_layout,
    render_header,
    render_face,
    render_vitals,
    render_radio,
    render_memory,
    render_missions,
    render_logs,
    render_prompt_bar,
    render_footer
)
from cli.dashboard.keyboard import KeyboardListener

log = logging.getLogger(__name__)

# Global TUI interactive state variables
chat_mode: bool = False
input_buffer: str = ""
gotchi_thinking: bool = False
thinking_verb: str = ""
active_face: str = "(o.o)"

# Global cache variables to ensure high performance
sys_dict = {}
gotchi_stats = {}
pwn_stats = {}
recent_logs = []
missions_data = {}
last_fetch_time = 0.0
fetch_lock = asyncio.Lock()

async def update_data_cache_task():
    """Concurrently fetches data from SQLite and hardware system status to populate local cache."""
    global sys_dict, gotchi_stats, pwn_stats, recent_logs, missions_data, last_fetch_time
    async with fetch_lock:
        try:
            sys_task = asyncio.create_task(fetch_system_stats())
            gotchi_task = asyncio.create_task(fetch_gotchi_stats())
            pwn_task = asyncio.create_task(fetch_pwn_status())
            logs_task = asyncio.create_task(fetch_recent_logs(8))
            missions_task = asyncio.create_task(fetch_missions_status())
            
            results = await asyncio.gather(sys_task, gotchi_task, pwn_task, logs_task, missions_task)
            sys_stats, gotchi_stats_res, pwn_stats_res, recent_logs_res, missions_data_res = results
            
            sys_dict = sys_stats.to_dict() if hasattr(sys_stats, 'to_dict') else {}
            gotchi_stats = gotchi_stats_res
            pwn_stats = pwn_stats_res
            recent_logs = recent_logs_res
            missions_data = missions_data_res
            last_fetch_time = time.time()
        except Exception as e:
            log.error(f"Failed to update dashboard data cache: {e}")

async def submit_chat_task(prompt: str):
    """Asynchronously calls the LLM, logs to system events, and awards XP in background."""
    global gotchi_thinking, thinking_verb, active_face, last_fetch_time
    
    gotchi_thinking = True
    verbs = [
        "grinding salts...",
        "reflecting on electromagnetic waves...",
        "calculating quantum XP rewards...",
        "tapping into global mesh...",
        "scanning sub-space radios...",
        "consulting with the AI gods..."
    ]
    thinking_verb = random.choice(verbs)
    active_face = random.choice(["(✜‿‿✜)", "(o.o)", "(•ิ_•ิ)"])
    
    try:
        from core.router import get_router
        from db.memory import get_history, save_message
        from config import get_admin_id
        from game_engine.vitals import add_xp
        from audit_logging.command_logger import log_command, log_bot_response
        
        admin_id = get_admin_id() or 0
        
        # 1. Log prompt to commands.jsonl so it shows up in "RECENT ACTIVITY" pane!
        log_command("message", admin_id, admin_id, username="TUI_Owner", text=prompt, source="tui")
        
        # 2. Fetch conversation history from DB
        db_history = get_history(admin_id, limit=8)
        
        # 3. Query Gotchi's LLM brain
        response, connector = await get_router().call(prompt, db_history)
        
        # 4. Save gotchi's response to database
        save_message(admin_id, "assistant", response)
        
        # 5. Log response to commands.jsonl so it shows up in "RECENT ACTIVITY" pane!
        log_bot_response(admin_id, response_preview=response, connector=connector)
        log_command("response", admin_id, admin_id, username="Gotchi", text=response, source="tui")
        
        # 6. Award +10 XP for user interaction
        add_xp(10, source="chat_interaction")
        
        # 7. Extract reaction (e.g. FACE: excited)
        face_match = re.search(r'FACE:\s*(\S+)', response)
        if face_match:
            face_name = face_match.group(1).strip().lower()
            from ui.faces import get_all_faces
            faces = get_all_faces()
            if face_name in faces:
                chosen = faces[face_name]
                active_face = random.choice(chosen) if isinstance(chosen, list) else chosen
            else:
                active_face = "(★ ◡ ★)"  # Default proud/happy face
        else:
            active_face = "(★ ◡ ★)"
            
    except Exception as e:
        from db.memory import save_message
        from config import get_admin_id
        from audit_logging.command_logger import log_error
        admin_id = get_admin_id() or 0
        save_message(admin_id, "assistant", f"Error: Failed to process thought: {e}")
        log_error("TUI_Chat_Error", str(e))
        active_face = "(✜‿‿✜)"
    finally:
        gotchi_thinking = False
        # Force a data refresh to pull the new gotchi message and updated XP
        last_fetch_time = 0.0

async def dashboard_loop(refresh_rate: float):
    global chat_mode, input_buffer, gotchi_thinking, thinking_verb, active_face
    global sys_dict, gotchi_stats, pwn_stats, recent_logs, missions_data, last_fetch_time
    
    console = Console()
    layout = generate_layout()
    kb = KeyboardListener()
    kb.start()
    
    # Run initial fetch so dashboard starts populated
    await update_data_cache_task()
    
    try:
        # Minimum terminal size required by the fixed layout (3+8+8+3+3 = 25 rows, 80 cols safe minimum)
        term_width, term_height = console.size
        if term_height < 26 or term_width < 60:
            raise RuntimeError(
                f"Terminal too small ({term_width}×{term_height}). "
                f"Please resize to at least 60 columns × 26 rows and try again."
            )

        # Loop at 10 FPS (0.1s) for lag-free typing; background IO is throttled inside the loop
        tui_tick = 0.1
        with Live(layout, console=console, screen=True, refresh_per_second=10) as live:
            while True:
                # Handle keyboard inputs
                key = kb.get_key()
                if key:
                    if chat_mode:
                        if key == "key:escape":
                            chat_mode = False
                            input_buffer = ""
                        elif key == "key:backspace":
                            input_buffer = input_buffer[:-1]
                        elif key == "key:enter":
                            if input_buffer.strip() and not gotchi_thinking:
                                from db.memory import save_message
                                from config import get_admin_id
                                admin_id = get_admin_id() or 0
                                
                                # Save user message to database
                                msg = input_buffer.strip()
                                save_message(admin_id, "user", msg)
                                
                                # Force immediate history refresh to show typed text
                                last_fetch_time = 0.0
                                
                                # Launch background query task
                                asyncio.create_task(submit_chat_task(msg))
                                input_buffer = ""
                        elif key.startswith("char:"):
                            char_val = key[len("char:"):]
                            if len(input_buffer) < 80:
                                input_buffer += char_val
                    else:
                        if key == "char:q":
                            break
                        elif key == "char:c":
                            chat_mode = True
                            input_buffer = ""
                        elif key == "char:p":
                            try:
                                from utils.ipc import state_manager
                                state_manager.update_key("paused_until", time.time() + 300)
                            except: pass
                
                # Dynamic throttled data fetching (once every 2 seconds, unless forced)
                current_time = time.time()
                if current_time - last_fetch_time > refresh_rate:
                    asyncio.create_task(update_data_cache_task())
                    # Prevent multiple overlapping fetches by setting last_fetch_time immediately
                    last_fetch_time = current_time
                
                # Periodic idle face updates to keep the gotchi "alive"
                if not gotchi_thinking and random.random() < 0.02: # check 2% chance per 0.1s tick
                    from ui.faces import get_all_faces
                    try:
                        faces = get_all_faces()
                        mood = random.choice(["idle", "smart", "happy", "excited", "bored"])
                        chosen = faces.get(mood, ["(o.o)"])
                        active_face = random.choice(chosen) if isinstance(chosen, list) else chosen
                    except:
                        pass
                
                # Update layout
                from core.router import get_router
                try:
                    is_lite = get_router().force_lite
                    mode_str = "Lite ⚡" if is_lite else "Pro 🧠"
                except:
                    mode_str = "Pro 🧠"
                    
                layout["header"].update(render_header(uptime=sys_dict.get('uptime', '?'), mode=mode_str))
                layout["face"].update(render_face(active_face))
                layout["vitals"].update(render_vitals(sys_dict))
                layout["right_col"].update(render_radio(pwn_stats))
                layout["memory"].update(render_memory(gotchi_stats))
                layout["missions"].update(render_missions(missions_data))
                layout["logs"].update(render_logs(recent_logs, gotchi_thinking, thinking_verb))
                layout["prompt_bar"].update(render_prompt_bar(chat_mode, input_buffer))
                layout["footer"].update(render_footer())
                
                await asyncio.sleep(tui_tick)
    finally:
        kb.stop()
        print("\033[H\033[J", end="")

def run_dashboard(refresh_rate: float = 2.0):
    try:
        asyncio.run(dashboard_loop(refresh_rate))
    except KeyboardInterrupt:
        print("\033[H\033[J", end="")
        print("Dashboard exited.")
