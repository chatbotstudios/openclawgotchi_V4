import logging
import os
import requests
from datetime import datetime, timezone
from core.commands import set_env_var
from hardware.display import update_display

log = logging.getLogger("Hardware.NightMode")

# Global cache for the current day's times
_solar_times = {
    "sunrise": None,
    "sunset": None,
    "last_fetch": None
}

def update_night_mode_state():
    """Check solar times and toggle DARK_MODE accordingly."""
    from config import _env_flag
    if not _env_flag("AUTO_NIGHT_MODE", False):
        return

    lat = os.environ.get("LATITUDE")
    lon = os.environ.get("LONGITUDE")
    
    if not lat or not lon:
        log.warning("NightMode: Missing LATITUDE/LONGITUDE. Cannot calculate solar times.")
        return

    # Fetch times if not cached for today
    today = datetime.now().date()
    if _solar_times["last_fetch"] != today:
        try:
            url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data["status"] == "OK":
                # API returns UTC ISO8601
                _solar_times["sunrise"] = datetime.fromisoformat(data["results"]["sunrise"])
                _solar_times["sunset"] = datetime.fromisoformat(data["results"]["sunset"])
                _solar_times["last_fetch"] = today
                log.info(f"🌙 NightMode: Solar times updated. Sunrise: {_solar_times['sunrise'].strftime('%H:%M')} UTC, Sunset: {_solar_times['sunset'].strftime('%H:%M')} UTC")
            else:
                log.error(f"NightMode API error: {data['status']}")
        except Exception as e:
            log.error(f"NightMode fetch failed: {e}")
            return

    if not _solar_times["sunrise"] or not _solar_times["sunset"]:
        return

    # Compare current UTC time
    now_utc = datetime.now(timezone.utc)
    
    # It is night if now < sunrise OR now > sunset
    is_night = now_utc < _solar_times["sunrise"] or now_utc > _solar_times["sunset"]
    
    current_dark = os.environ.get("DARK_MODE", "0") == "1"
    
    if is_night and not current_dark:
        log.info("🌙 Night detected. Activating Dark Mode.")
        set_env_var("DARK_MODE", "1")
        os.environ["DARK_MODE"] = "1"
        update_display(full_refresh=True)
    elif not is_night and current_dark:
        log.info("☀️ Day detected. Deactivating Dark Mode.")
        set_env_var("DARK_MODE", "0")
        os.environ["DARK_MODE"] = "0"
        update_display(full_refresh=True)

async def night_mode_loop():
    """Background task for periodic night mode checks."""
    import asyncio
    while True:
        try:
            update_night_mode_state()
        except Exception as e:
            log.error(f"NightMode loop error: {e}")
        await asyncio.sleep(900) # Check every 15 minutes
