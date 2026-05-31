import logging
from hooks.runner import hook, HookEvent
from src.game_engine.state import load_state, save_state
from src.game_engine.vitals import calculate_hp, add_xp
from src.game_engine.missions import complete_mission

log = logging.getLogger(__name__)

@hook("heartbeat")
def aipet_heartbeat_hook(event: HookEvent):
    """Calculates HP and triggers Uptime Resilience on heartbeat."""
    state = load_state()
    # Mocking hardware vitals for now (this would normally read from actual system stats)
    cpu = 15.0
    mem = 40.0
    uptime_hours = 25.0
    battery = 85.0
    
    new_hp = calculate_hp(cpu, mem, uptime_hours, battery)
    
    if new_hp != state.hp:
        state.hp = new_hp
        save_state(state)
        log.debug(f"AIPET HP updated to {new_hp:.1f}")

    # Example: Completing 'Uptime Resilience' if uptime is good
    if uptime_hours > 24.0:
        complete_mission("Uptime Resilience")

@hook("pwn.handshake")
def aipet_handshake_hook(event: HookEvent):
    """Hook to capture XP for Radio Collector mission."""
    # Award minor XP for each handshake
    add_xp(10, source="handshake_capture")
    
    # Mark mission complete (in a real system this would track progress rather than immediate completion)
    complete_mission("Radio Collector")

@hook("message")
def aipet_message_hook(event: HookEvent):
    """Hook to track reasoning or interactions for Cortex Calibration."""
    if event.user_id:  # Valid interaction
        complete_mission("Cortex Calibration")
