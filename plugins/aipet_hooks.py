import logging
from hooks.runner import hook, HookEvent
from src.game_engine.state import load_state, save_state
from src.game_engine.vitals import calculate_hp, add_xp
from src.game_engine.missions import increment_mission_progress

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

    # Example: Increment 'Ironclad Uptime' if uptime is good (in a real system, this increments by hours)
    if uptime_hours >= 1.0:
        increment_mission_progress("Ironclad Uptime", 1)

@hook("pwn.handshake")
def aipet_handshake_hook(event: HookEvent):
    """Hook to capture XP for Handshake Hunter mission."""
    # Award minor XP for each handshake
    add_xp(5, source="handshake_capture")
    
    # Increment mission progress
    increment_mission_progress("Handshake Hunter", 1)

@hook("message")
def aipet_message_hook(event: HookEvent):
    """Hook to track reasoning or interactions for Deep Thought."""
    if event.user_id:  # Valid interaction
        increment_mission_progress("Deep Thought", 1)
