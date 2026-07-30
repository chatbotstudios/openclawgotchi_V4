"""
System stats — temperature, memory, uptime.
"""

import os
from dataclasses import dataclass

import psutil


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
    
    # 1. Uptime — /proc/uptime (no subprocess)
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        if days > 0:
            stats.uptime = f"up {days} days, {hours}:{minutes:02d}"
        else:
            stats.uptime = f"up {hours}:{minutes:02d}"
    except Exception:
        stats.uptime = "?"
    
    # 2. Temperature — /sys/class/thermal/thermal_zone0/temp (no subprocess)
    try:
        if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                stats.temp = f"{int(f.read().strip())/1000:.1f}°C"
        else:
            # Fallback to psutil sensors_temperatures
            temps = psutil.sensors_temperatures()
            if temps:
                for entries in temps.values():
                    if entries:
                        stats.temp = f"{entries[0].current}°C"
                        break
    except Exception:
        pass
    
    # 3. Memory — /proc/meminfo (no subprocess)
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    avail_mb = int(line.split()[1]) / 1024
                    stats.memory = f"Free: {avail_mb:.1f} MB"
                    break
    except Exception:
        try:
            vm = psutil.virtual_memory()
            stats.memory = f"Free: {vm.available / (1024*1024):.1f} MB"
        except Exception:
            pass
    
    # 4. CPU Load — psutil (already no subprocess)
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
        from config import DB_PATH, PROJECT_DIR
        paths_info = f"[PATHS] Project: {PROJECT_DIR} | DB: {DB_PATH}"
    except Exception:
        paths_info = ""
    
    return f"{self_info}\n[SYSTEM] Uptime: {stats.uptime} | Temp: {stats.temp} | RAM: {stats.memory}\n{paths_info}"
