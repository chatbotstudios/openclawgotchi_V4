from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich import box

def generate_layout() -> Layout:
    """Create the base grid layout with fixed compact sizes."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="top_row", size=8),
        Layout(name="bottom_row", size=8),
        Layout(name="footer", size=3)
    )
    
    layout["top_row"].split_row(
        Layout(name="face", ratio=2),
        Layout(name="vitals", ratio=3),
        Layout(name="right_col", ratio=3)
    )
    
    layout["bottom_row"].split_row(
        Layout(name="memory", ratio=2),
        Layout(name="missions", ratio=3),
        Layout(name="logs", ratio=4)
    )
    
    return layout

def render_header(uptime: str = "?", mode: str = "Pro 🧠") -> Panel:
    header_text = Text()
    header_text.append("🦋 OPENCLAWGOTCHI V4", style="bold cyan")
    header_text.append(f"  |  MODE: {mode}  |  UPTIME: {uptime}  |  ", style="white")
    header_text.append("[LIVE 🔴]", style="bold red blink")
    return Panel(header_text, style="white on black")

def render_face(face_str: str) -> Panel:
    ascii_art = f"\n\n       {face_str}\n\n"
    return Panel(Align.center(ascii_art, vertical="middle"), title="🤖 E-INK SIMULATOR", border_style="cyan")

def render_vitals(sys_stats: dict) -> Panel:
    table = Table(box=box.SIMPLE, show_header=False, expand=True)
    table.add_column("Key", style="bold cyan", width=6)
    table.add_column("Value", style="white")
    
    table.add_row("CPU:", sys_stats.get('cpu_load', '?'))
    table.add_row("RAM:", sys_stats.get('memory', '?'))
    
    temp = sys_stats.get('temp', '?')
    temp_style = "white"
    if "°C" in temp:
        try:
            val = float(temp.replace("°C", ""))
            if val > 75: temp_style = "bold red"
            elif val > 60: temp_style = "bold yellow"
        except: pass
        
    table.add_row("TEMP:", Text(temp, style=temp_style))
    
    return Panel(table, title="📊 SYSTEM VITALS", border_style="green")

def render_radio(pwn_stats: dict) -> Panel:
    table = Table(box=box.SIMPLE, show_header=False, expand=True)
    table.add_column("Key", style="bold cyan")
    table.add_column("Value", style="white")
    
    status = pwn_stats.get("status", "OFFLINE")
    table.add_row("WiFi:", Text(status, style="bold green" if status == "ONLINE" else "bold red"))
    table.add_row("APs:", f"{pwn_stats.get('aps', 0)} tracking")
    table.add_row("BLE:", f"{pwn_stats.get('ble', 0)} devices")
    table.add_row("Pcaps:", f"{pwn_stats.get('handshakes', 0)} handshakes")
    
    target = pwn_stats.get("state", {}).get("target_lock", "None")
    table.add_row("Target:", target)
    
    # Paused status
    import time
    paused_until = pwn_stats.get("state", {}).get("paused_until", 0)
    if time.time() < paused_until:
        rem = int(paused_until - time.time())
        table.add_row("State:", f"Paused ({rem}s)")
        
    return Panel(table, title="📡 RADIO & PWN", border_style="magenta")

def render_memory(gotchi_stats: dict) -> Panel:
    text = Text()
    text.append(f"• Level: {gotchi_stats.get('level', '?')} ({gotchi_stats.get('title', '?')})\n")
    text.append(f"• XP: {gotchi_stats.get('xp', '?')}\n")
    text.append(f"• Msgs: {gotchi_stats.get('messages', '?')}")
    return Panel(text, title="🧠 BRAIN & XP", border_style="yellow")

def render_missions(missions_data: dict) -> Panel:
    text = Text()
    active_list = missions_data.get("active", [])
    completed_count = missions_data.get("completed_count", 0)
    pending_count = missions_data.get("pending_count", 0)
    
    text.append("Active Targets:\n", style="bold cyan")
    if not active_list:
        text.append(" • No active missions!\n", style="italic white")
    else:
        for m in active_list:
            name = m.get("name", "Unknown")
            category = m.get("category", "General")
            progress = m.get("progress", 0)
            target = m.get("target", 1)
            xp = m.get("xp", 0)
            
            text.append(f" • [{category}] {name} ({progress}/{target}) ", style="white")
            text.append(f"+{xp}XP\n", style="bold yellow")
            
    text.append("\n")
    text.append(f"🏆 Done: {completed_count}  |  ⏳ Pend: {pending_count}", style="bold green")
    
    return Panel(text, title="🎯 TARGET MISSIONS", border_style="cyan")

def render_logs(logs: list) -> Panel:
    text = Text.from_markup("\n".join(logs))
    return Panel(text, title="📜 RECENT ACTIVITY", border_style="blue")

def render_footer(chat_mode: bool = False, input_buffer: str = "") -> Panel:
    if chat_mode:
        text = Text()
        text.append("💬 Talk to Gotchi (ESC to exit): ", style="bold cyan")
        text.append(input_buffer, style="white")
        text.append("█", style="dim")  # simulated cursor
        return Panel(text, style="black on bright_yellow")
    else:
        text = "[Q]uit  |  [R]efresh  |  [P]ause Pwn  |  [C]hat Mode"
        return Panel(Align.center(text), style="black on white")
