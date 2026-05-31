import logging
from hooks.runner import hook, HookEvent
from core.missions.manager import get_missions, increment_mission_progress

log = logging.getLogger(__name__)

def process_event_for_missions(trigger_name: str, amount: int = 1):
    """Helper to check all active missions for a specific trigger."""
    active = get_missions("active")
    for m in active:
        if m.trigger_event == trigger_name:
            try:
                increment_mission_progress(m.id, amount)
            except Exception as e:
                log.error(f"Failed to update mission {m.id}: {e}")

@hook("message")
def track_message_mission(event: HookEvent):
    """Track message-based missions."""
    process_event_for_missions("message")

@hook("heartbeat")
def track_heartbeat_mission(event: HookEvent):
    """Track survival/uptime missions."""
    process_event_for_missions("heartbeat")

# For wifi events, normally these would be triggered by Bettercap parsers
@hook("wifi_handshake")
def track_handshake_mission(event: HookEvent):
    """Track handshake captures."""
    process_event_for_missions("wifi.handshake.captured")
