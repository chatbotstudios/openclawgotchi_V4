import logging
from hooks.runner import hook, HookEvent
from game_engine.state import load_state, save_state
from game_engine.vitals import calculate_hp, add_xp, decay_mood
from game_engine.missions import increment_mission_progress

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

    # Mood decay
    decay_mood()

    # Example: Increment 'Ironclad Uptime' if uptime is good (in a real system, this increments by hours)
    if uptime_hours >= 1.0:
        increment_mission_progress("Ironclad Uptime", 1, event=event)

@hook("pwn.handshake")
def aipet_handshake_hook(event: HookEvent):
    """Hook to capture XP for Handshake Hunter mission."""
    # Award minor XP for each handshake
    add_xp(5, source="handshake_capture")
    
    # Increment mission progress
    increment_mission_progress("Handshake Hunter", 1, event=event)

@hook("pwn.ble")
def aipet_ble_hook(event: HookEvent):
    """Hook to track BLE Phantom mission progress on each BLE scan."""
    if event.action == "scan":
        device_count = event.data.get("device_count", 0)
        log.info(f"BLE scan completed — {device_count} devices found. Incrementing BLE Phantom.")
        increment_mission_progress("BLE Phantom", 1, event=event)
        # Award small XP for each scan with devices
        if device_count > 0:
            add_xp(3, source="ble_scan")

@hook("message")
def aipet_message_hook(event: HookEvent):
    """Hook to track reasoning, Chatterbox, and Night Owl interactions."""
    if event.user_id:  # Valid interaction
        increment_mission_progress("Deep Thought", 1, event=event)
        increment_mission_progress("Chatterbox", 1, event=event)
        
        # Check Night Owl (between 2 AM and 4 AM)
        if 2 <= event.timestamp.hour < 4:
            increment_mission_progress("Night Owl", 1, event=event)

@hook("command")
def aipet_command_hook(event: HookEvent):
    """Hook to track command usage for automation and admin missions."""
    if not event.user_id:
        return
        
    action = event.action.lower()
    
    if action in ("/remember",):
        increment_mission_progress("The Teacher", 1, event=event)
    elif action in ("/recall",):
        increment_mission_progress("The Historian", 1, event=event)
    elif action in ("/status", "/memory", "/health"):
        increment_mission_progress("System Admin", 1, event=event)
    elif action in ("/cron", "/jobs"):
        increment_mission_progress("Cron Master", 1, event=event)
