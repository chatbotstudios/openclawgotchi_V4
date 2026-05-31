from hooks.runner import hook, HookEvent
import logging

log = logging.getLogger("Plugins")

@hook("pwn.handshake")
def on_handshake(event: HookEvent):
    log.info(f"PLUGIN: Hello! I see a handshake for {event.data.get('ap')}!")
    # You can trigger hardware or UI changes here
    from hardware.display import update_display
    update_display(mood="celebrate", text="Plugin: Handshake captured!")

@hook("pwn.event")
def on_any_event(event: HookEvent):
    # This runs for EVERY Bettercap event
    if event.action == "mod.mesh.peer":
        log.info(f"PLUGIN: Peer detected: {event.data.get('name')}")
