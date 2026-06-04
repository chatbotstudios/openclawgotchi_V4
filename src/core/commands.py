import logging
from core.router import get_router
from hardware.system import get_stats
from db.stats import get_stats_summary
from db.memory import clear_history, get_message_count
from core.registry import get_tools_and_schemas
from hardware.display import show_face
from config import BOT_NAME, PROJECT_DIR
from sdk.tool_builder import register_tool

log = logging.getLogger(__name__)

def set_env_var(key: str, value: str):
    """Safely updates a variable in the .env file."""
    env_file = PROJECT_DIR / ".env"
    lines = []
    if env_file.exists():
        with open(env_file, "r") as f:
            lines = f.readlines()
            
    new_line = f"{key}={value}\n"
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = new_line
            found = True
            break
    if not found:
        lines.append(new_line)
        
    with open(env_file, "w") as f:
        f.writelines(lines)
    return True

@register_tool
def get_status_report(chat_id: int = None):
    """
    Gathers hardware and bot stats into a structured report. 
    Use this to check your own Level, XP, CPU Temperature, and Memory.
    """
    stats = get_stats()
    gotchi_stats = get_stats_summary()
    router = get_router()
    mode = "Lite ⚡" if router.force_lite else "Pro 🧠"
    
    _, schemas = get_tools_and_schemas()
    skills_count = len(schemas) if schemas else 0
    
    msg_count = get_message_count(chat_id) if chat_id else 0
    
    # RPG-style XP progress bar (10 segments)
    xp_in = gotchi_stats.get("xp_in_level", 0)
    xp_need = gotchi_stats.get("xp_needed_this_level") or 1
    max_lv = gotchi_stats.get("max_level", 20)
    
    if gotchi_stats["level"] >= max_lv:
        xp_bar = "█" * 10 + " MAX"
    else:
        filled = min(10, int(10 * xp_in / xp_need)) if xp_need else 0
        xp_bar = "█" * filled + "░" * (10 - filled)
        xp_bar += f" {xp_in}/{xp_need}"

    report = {
        "bot_name": BOT_NAME,
        "level": gotchi_stats["level"],
        "title": gotchi_stats["title"],
        "xp": gotchi_stats["xp"],
        "xp_bar": xp_bar,
        "uptime": stats.uptime,
        "temp": stats.temp,
        "memory": stats.memory,
        "mode": mode,
        "skills": skills_count,
        "messages": msg_count,
        "days_alive": gotchi_stats.get("days_alive", 0)
    }
    return report

def format_status_markdown(report):
    """Formats the status report for Discord/Markdown."""
    msg = (
        f"🎮 *Lv{report['level']} {report['title']}*\n"
        f"XP: {report['xp']} | {report['xp_bar']}\n"
        f"Days: {report['days_alive']} | Msgs: {report['messages']}\n\n"
        f"*System*\n"
        f"⏱ {report['uptime']} | 🌡 {report['temp']}\n"
        f"💾 {report['memory']}\n\n"
        f"*Bot*\n"
        f"Mode: {report['mode']}\n"
        f"Skills: {report['skills']}"
    )
    return msg

def format_status_plain(report):
    """Formats the status report for SSH/Plaintext."""
    return (
        f"--- {report['bot_name'].upper()} STATUS ---\n"
        f"Level: {report['level']} ({report['title']})\n"
        f"XP: {report['xp']} [{report['xp_bar']}]\n"
        f"Mode: {report['mode']}\n"
        f"Uptime: {report['uptime']}\n"
        f"Temp: {report['temp']}\n"
        f"Memory: {report['memory']}\n"
        f"Skills: {report['skills']}"
    )

@register_tool
def set_llm_mode(mode_name: str = None):
    """
    Sets the LLM mode (lite or pro). 
    Use 'lite' for simple tasks and 'pro' for complex reasoning/coding.
    Pass no arguments to toggle.
    """
    router = get_router()
    
    if mode_name and mode_name.lower() == "lite":
        new_lite = True
    elif mode_name and mode_name.lower() == "pro":
        new_lite = False
    else:
        # Toggle
        new_lite = not router.force_lite
    
    router.force_lite = new_lite
    
    # Persist choice
    set_env_var("LLM_FORCE_LITE", "1" if new_lite else "0")
    
    msg = f"✅ Mode switched to: {'LITE (Flash)' if new_lite else 'PRO (Reasoning)'}"
    log.info(msg)
    return msg, new_lite

def clear_bot_history(chat_id):
    """Wipes conversation history for a context."""
    clear_history(chat_id)
    return True

def get_tactical_dashboard():
    """Gathers real-time data for the terminal tactical dashboard."""
    from extensions.pwn.wifi import pwn_status
    from extensions.pwn.ble import pwn_ble_scan
    from hardware.display import get_current_face_ascii
    
    wifi = pwn_status()
    ble = pwn_ble_scan()
    face = get_current_face_ascii()
    
    return {
        "wifi": wifi,
        "ble": ble,
        "face": face,
        "stats": get_stats()
    }

@register_tool
def create_reminder(message: str) -> str:
    """Creates a one-shot reminder that the bot will display and remember."""
    show_face("happy", f"REMINDER: {message}")
    return f"Reminder set: {message}"

@register_tool
def manage_cron(action: str, task: str = None, schedule: str = None) -> str:
    """Manage recurring tasks (cron jobs). Actions: list, add, delete."""
    import subprocess
    if action == "list":
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        lines = [line for line in result.stdout.splitlines() if "gotchi" in line]
        return "\n".join(lines) if lines else "No bot tasks scheduled."
    
    elif action == "add":
        if not task or not schedule: return "Missing task or schedule."
        cmd = f"(crontab -l 2>/dev/null; echo '{schedule} /usr/local/bin/gotchi say \"RECURRING: {task}\" # gotchi_task') | crontab -"
        subprocess.run(cmd, shell=True)
        return f"Recurring task added: '{task}' at '{schedule}'"
    
    elif action == "delete":
        cmd = "crontab -l | grep -v 'gotchi_task' | crontab -"
        subprocess.run(cmd, shell=True)
        return "All bot tasks deleted."
    
    return "Invalid action."


@register_tool
def manage_net(action: str, ssid: str = None, password: str = None) -> str:
    """Manage Wi-Fi connections and diagnostics. Actions: scan, add, connect, list, status, restart, ping, dns, routes."""
    from core.radio import manage_net as radio_net
    return radio_net(action, ssid, password)

@register_tool
def manage_wifi_interface(action: str) -> str:
    """Manage Wi-Fi connectivity. Actions: on (Managed/Internet), off (Monitor/Tactical), status, scan."""
    from core.radio import manage_wifi_interface as radio_wifi
    return radio_wifi(action)

@register_tool
def manage_ble_adapter(action: str, value: str = None) -> str:
    """Manage Bluetooth adapter state and broadcasting. Actions: on, off, status, scan, info, broadcast."""
    from core.radio import manage_ble_adapter as radio_ble
    return radio_ble(action, value)

@register_tool
def manage_reminders(action: str, msg: str = None) -> str:
    """Manage one-shot reminders. Actions: add, list, delete."""
    # For now, reminders are just displayed. In a full system, these would be in DB.
    if action == "add":
        from hardware.display import show_face
        show_face("happy", f"REMINDER: {msg}")
        return f"Reminder set: {msg}"
    return "Reminder management active (Basic)."

@register_tool
def launch_offline_hunt(duration_minutes: int) -> str:
    """
    Launch an autonomous offline handshake hunt.
    This disconnects from the internet (entering monitor mode) for the given duration.
    It runs safely in the background and will automatically reconnect when finished.
    """
    import subprocess
    import sys
    
    duration_seconds = int(duration_minutes) * 60
    cmd = [
        sys.executable, "-c",
        f"from core.offline_hunter import offline_hunter; offline_hunter.run_hunt({duration_seconds}, 'handshake_hunter_v1')"
    ]
    
    # Run completely detached from the caller so it doesn't block Litellm
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return f"🚀 Offline Hunt launched in background for {duration_minutes} minutes. Connection will drop shortly and restore automatically."

# Removed duplicate set_llm_mode

@register_tool
def recall_memory(query: str) -> str:
    """Search the bot's long-term memory for specific keywords."""
    from db.memory import search_facts
    facts = search_facts(query)
    if not facts:
        return f"I have no memory of '{query}'."
    
    lines = [f"🧠 Memory Recall for '{query}':"]
    for f in facts[:10]:
        lines.append(f"• {f['content']} ({f['timestamp']})")
    return "\n".join(lines)
