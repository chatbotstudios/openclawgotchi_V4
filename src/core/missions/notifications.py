import logging
import threading
import requests
from config import DISCORD_BOT_TOKEN, DISCORD_HEARTBEATS_CHANNEL
from core.missions.models import Mission

log = logging.getLogger(__name__)

def _send_discord_webhook(payload: dict):
    if not DISCORD_BOT_TOKEN or not DISCORD_HEARTBEATS_CHANNEL or DISCORD_HEARTBEATS_CHANNEL == "0":
        return
    try:
        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        r = requests.post(
            f"https://discord.com/api/v10/channels/{DISCORD_HEARTBEATS_CHANNEL}/messages",
            headers=headers,
            json=payload,
            timeout=5
        )
        r.raise_for_status()
    except Exception as e:
        log.warning(f"Failed to broadcast mission to Discord: {e}")

def notify_discord_mission(mission: Mission, new_status: str):
    """Fire and forget discord notification."""
    if new_status == 'active':
        content = f"🎯 **Mission Accepted!**\n> **{mission.title}**\n> {mission.description}"
    elif new_status == 'completed':
        content = f"🏆 **Mission Complete!**\n> **{mission.title}**\n> {mission.description}\n*+{mission.reward_xp} XP gained!*"
    elif new_status == 'abandoned':
        content = f"❌ **Mission Abandoned!**\n> **{mission.title}**"
    else:
        return # Do nothing for 'available'

    payload = {"content": content}
    
    # Run in a background thread to prevent blocking SQLite or CLI
    t = threading.Thread(target=_send_discord_webhook, args=(payload,))
    t.daemon = True
    t.start()
