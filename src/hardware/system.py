"""
System stats — temperature, memory, uptime.
"""

import subprocess
import os
import psutil
from dataclasses import dataclass


@dataclass
class SystemStats:
    uptime: str = "?"
    temp: str = "?"
    memory: str = "?"
    cpu_load: str = "?"
    
    def __str__(self) -> str:
        return f"Uptime: {self.uptime} | Temp: {self.temp} | RAM: {self.memory} | CPU: {self.cpu_load}"
    
    def to_dict(self) -> dict:
        return {"uptime": self.uptime, "temp": self.temp, "memory": self.memory, "cpu_load": self.cpu_load}


def get_stats() -> SystemStats:
    """Gather current system stats."""
    stats = SystemStats()
    
    # 1. Uptime
    try:
        # psutil approach for uptime
        import time
        uptime_seconds = time.time() - psutil.boot_time()
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            stats.uptime = f"up {days} days, {hours}:{minutes:02d}"
        else:
            stats.uptime = f"up {hours}:{minutes:02d}"
    except Exception:
        # Fallback to shell
        try:
            result = subprocess.run(["uptime", "-p"], capture_output=True, text=True, timeout=2)
            stats.uptime = result.stdout.strip()
        except: pass
    
    # 2. Temperature
    try:
        # Try vcgencmd first (Raspberry Pi specific)
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            stats.temp = result.stdout.strip().replace("temp=", "")
        else:
            # Fallback to psutil sensors_temperatures (may work on some macOS/Linux)
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        stats.temp = f"{entries[0].current}°C"
                        break
            
            if stats.temp == "?":
                # Fallback for Linux thermal zone
                if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                        stats.temp = f"{int(f.read().strip())/1000:.1f}°C"
    except Exception:
        pass
    
    # 3. Memory
    try:
        vm = psutil.virtual_memory()
        stats.memory = f"Free: {vm.available / (1024*1024):.1f} MB"
    except Exception:
        try:
            result = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                stats.memory = f"Free: {result.stdout.splitlines()[1].split()[6]}"
        except: pass
    
    # 4. CPU Load
    try:
        load = psutil.cpu_percent(interval=None)
        stats.cpu_load = f"{load}%"
    except Exception:
        pass
    
    return stats


def get_stats_string() -> str:
    """Get stats as formatted string for prompts (with self-awareness)."""
    stats = get_stats()
    
    # Add gotchi stats for self-awareness
    try:
        from db.stats import get_stats_summary
        g = get_stats_summary()
        self_info = f"[SELF] Level {g['level']} {g['title']} | XP: {g['xp']} | Messages: {g['messages']}"
    except Exception:
        self_info = "[SELF] Stats loading..."
    
    try:
        from config import PROJECT_DIR, DB_PATH
        paths_info = f"[PATHS] Project: {PROJECT_DIR} | DB: {DB_PATH}"
    except Exception:
        paths_info = ""
    
    return f"{self_info}\n[SYSTEM] Uptime: {stats.uptime} | Temp: {stats.temp} | RAM: {stats.memory}\n{paths_info}"
