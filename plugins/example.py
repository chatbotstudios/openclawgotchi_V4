import logging
from hooks.runner import hook, HookEvent
from hardware.display import update_display

# Metadata
__author__ = 'evilsocket@gmail.com'
__version__ = '1.0.0'
__license__ = 'GPL3'
__description__ = 'A port of the Pwnagotchi example plugin for OpenClawGotchi V2.'

log = logging.getLogger("Plugins.Example")

@hook("startup")
def on_loaded(event: HookEvent):
    log.info("Example plugin loaded and initialized.")

@hook("pwn.ready")
def on_ready(event: HookEvent):
    log.info("Nervous System is ready and connected to Bettercap.")
    # In OpenClaw, we use update_display to change the face/text
    update_display(mood="happy", text="SAY: Example Plugin Ready!")

@hook("pwn.wifi_update")
def on_wifi_update(event: HookEvent):
    log.info(f"WiFi Update: Spotted new AP {event.data.get('hostname')}")

@hook("pwn.handshake")
def on_handshake(event: HookEvent):
    ap = event.data.get('ap')
    log.info(f"Handshake Captured: Successfully pwned {ap}!")
    update_display(mood="celebrate", text=f"SAY: Captured {ap}!")

@hook("pwn.peer_detected")
def on_peer_detected(event: HookEvent):
    peer = event.data.get('name')
    log.info(f"Peer Detected: I see {peer} nearby.")
    update_display(mood="found_peer", text=f"SAY: Hello {peer}!")

@hook("heartbeat")
def on_heartbeat(event: HookEvent):
    # This runs periodically (every 6h by default)
    log.debug("Example plugin received system heartbeat.")

@hook("pwn.event")
def on_any_event(event: HookEvent):
    # Catch-all for events we haven't explicitly mapped yet
    # event.action contains the Bettercap tag
    if event.action == "ble.device.new":
         log.debug(f"New BLE device found: {event.data.get('mac')}")
