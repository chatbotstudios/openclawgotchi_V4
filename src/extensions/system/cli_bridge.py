import os
import subprocess
import logging
import psutil
from pathlib import Path
from config import PROJECT_DIR
from sdk.tool_builder import register_tool
from core.commands import get_status_report, format_status_plain, set_llm_mode
from extensions.system.commands import _is_dangerous_command

log = logging.getLogger(__name__)

def _get_tree(path: Path, prefix: str = "", depth: int = 0, max_depth: int = 3) -> str:
    if depth > max_depth:
        return ""
    
    output = ""
    try:
        items = sorted([p for p in path.iterdir() if not p.name.startswith(('.', '__'))])
        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = "└── " if is_last else "├── "
            
            if item.is_dir():
                output += f"{prefix}{connector}{item.name}/\n"
                new_prefix = prefix + ("    " if is_last else "│   ")
                output += _get_tree(item, new_prefix, depth + 1, max_depth)
            else:
                size = item.stat().st_size
                size_str = f"{size} B"
                if size > 1024 * 1024:
                    size_str = f"{size / (1024*1024):.1f} MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f} KB"
                output += f"{prefix}{connector}{item.name} ({size_str})\n"
    except Exception as e:
        output += f"{prefix} ERROR: {e}\n"
    return output

def _i2c_scan() -> str:
    """Perform a scan of the I2C bus."""
    try:
        # Check if i2cdetect is available
        result = subprocess.run(["which", "i2cdetect"], capture_output=True, text=True)
        if result.returncode == 0:
            res = subprocess.run(["i2cdetect", "-y", "1"], capture_output=True, text=True)
            return res.stdout
    except:
        pass
    
    return "I2C Scan: Bus 1 unavailable or i2c-tools not installed.\n(Target: SHTC3 at 0x70, E-Ink at 0x3C/0x3D expected on Pi)"

def _ram_info() -> str:
    vm = psutil.virtual_memory()
    proc = psutil.Process(os.getpid())
    bot_mem = proc.memory_info().rss / (1024 * 1024)
    
    return (
        f"--- RAM INFO ---\n"
        f"System Total: {vm.total / (1024*1024):.1f} MB\n"
        f"System Free:  {vm.available / (1024*1024):.1f} MB ({vm.percent}% used)\n"
        f"Bot Usage:    {bot_mem:.1f} MB (PID: {os.getpid()})\n"
    )

@register_tool
def run_cli(command: str) -> str:
    """
    Access the Gotchi Command Center. Execute internal diagnostics or shell commands.
    Internal commands:
    - help: Show this menu.
    - status: RPG stats, Level, XP, and system health summary.
    - doctor: Run full system health check (internet, disk, temp, logs).
    - ls_r [path]: Recursive tree view of a directory.
    - ram_info: Detailed memory breakdown.
    - i2c_scan: Scan hardware bus for sensors/display.
    - df: Disk usage statistics.
    - uptime: How long the system has been running.
    - mode [lite|pro]: Switch between LLM reasoning modes.
    
    Fallback: Executes as a standard bash command.
    """
    if not command:
        return "Error: Empty command"
    
    cmd_parts = command.strip().split()
    base_cmd = cmd_parts[0].lower()
    args = cmd_parts[1:]

    # 1. Internal Command Routing
    if base_cmd == "help":
        return run_cli.__doc__.strip()
    
    elif base_cmd == "status":
        report = get_status_report()
        return format_status_plain(report)
    
    elif base_cmd == "doctor":
        try:
            doc_path = PROJECT_DIR / "src" / "utils" / "doctor.py"
            res = subprocess.run(["python3", str(doc_path)], capture_output=True, text=True, timeout=30)
            return f"--- DOCTOR REPORT ---\n{res.stdout}\n{res.stderr}"
        except Exception as e:
            return f"Doctor failed: {e}"
            
    elif base_cmd == "ls_r":
        target = Path(args[0]) if args else PROJECT_DIR
        if not target.is_absolute():
            target = (PROJECT_DIR / target).resolve()
        return f"ROOT: {target}\n" + _get_tree(target)
    
    elif base_cmd == "ram_info":
        return _ram_info()
    
    elif base_cmd == "i2c_scan":
        return _i2c_scan()
    
    elif base_cmd == "df":
        res = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
        return res.stdout
    
    elif base_cmd == "uptime":
        res = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
        return f"System {res.stdout.strip()}"
    
    elif base_cmd == "mode":
        mode_target = args[0] if args else None
        _, is_lite = set_llm_mode(mode_target)
        return f"LLM Mode set to: {'Lite' if is_lite else 'Pro'}"

    # 2. Fallback to Bash
    if _is_dangerous_command(command):
        return "Error: Command blocked for safety."
    
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=30, cwd=str(PROJECT_DIR)
        )
        out = result.stdout + result.stderr
        return out[:4000] if out else "(no output)"
    except Exception as e:
        return f"Error: {e}"
