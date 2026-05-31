import asyncio
import time
from rich.live import Live
from rich.console import Console

from cli.dashboard.fetchers import (
    fetch_system_stats,
    fetch_gotchi_stats,
    fetch_pwn_status,
    fetch_recent_logs,
    fetch_face
)
from cli.dashboard.layout import (
    generate_layout,
    render_header,
    render_face,
    render_vitals,
    render_radio,
    render_memory,
    render_logs,
    render_footer
)
from cli.dashboard.keyboard import KeyboardListener

async def dashboard_loop(refresh_rate: float):
    console = Console()
    layout = generate_layout()
    kb = KeyboardListener()
    kb.start()
    
    try:
        with Live(layout, console=console, screen=True, refresh_per_second=1.0/refresh_rate) as live:
            while True:
                # Handle keystrokes
                key = kb.get_key()
                if key == 'q':
                    break
                elif key == 'p':
                    # Pause PwnDaemon for 5 mins
                    try:
                        from utils.ipc import state_manager
                        state_manager.update_key("paused_until", time.time() + 300)
                    except: pass
                elif key == 'r':
                    # Force refresh
                    pass
                
                # Fetch data concurrently
                sys_task = asyncio.create_task(fetch_system_stats())
                gotchi_task = asyncio.create_task(fetch_gotchi_stats())
                pwn_task = asyncio.create_task(fetch_pwn_status())
                logs_task = asyncio.create_task(fetch_recent_logs(5))
                face_task = asyncio.create_task(fetch_face())
                
                results = await asyncio.gather(sys_task, gotchi_task, pwn_task, logs_task, face_task)
                sys_stats, gotchi_stats, pwn_stats, recent_logs, face_str = results
                
                sys_dict = sys_stats.to_dict() if hasattr(sys_stats, 'to_dict') else {}
                
                # Update layout
                from core.router import get_router
                try:
                    is_lite = get_router().force_lite
                    mode_str = "Lite ⚡" if is_lite else "Pro 🧠"
                except:
                    mode_str = "Pro 🧠"
                    
                layout["header"].update(render_header(uptime=sys_dict.get('uptime', '?'), mode=mode_str))
                layout["face"].update(render_face(face_str))
                layout["vitals"].update(render_vitals(sys_dict))
                layout["right_col"].update(render_radio(pwn_stats))
                layout["memory"].update(render_memory(gotchi_stats))
                layout["logs"].update(render_logs(recent_logs))
                layout["footer"].update(render_footer())
                
                await asyncio.sleep(refresh_rate)
    finally:
        kb.stop()
        # Clean up screen
        print("\033[H\033[J", end="")

def run_dashboard(refresh_rate: float = 2.0):
    try:
        asyncio.run(dashboard_loop(refresh_rate))
    except KeyboardInterrupt:
        print("\033[H\033[J", end="")
        print("Dashboard exited.")
