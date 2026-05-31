import asyncio
import websockets
import json
import logging
from threading import Thread

# Import OpenClawGotchi internals
from hardware.display import update_display
from db.memory import add_fact
from hooks.runner import run_hook, HookEvent

log = logging.getLogger("NervousSystem")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Fallback config
try:
    from config import BETTERCAP_USER, BETTERCAP_PASS
except ImportError:
    BETTERCAP_USER = "gotchi"
    BETTERCAP_PASS = "123456"

class NervousSystem:
    """
    The Nervous System connects the Subconscious (Bettercap) to the Ego (LLM / UI).
    It listens to the WebSocket event stream and triggers physical reflexes.
    """
    def __init__(self):
        self.ws_uri = f"ws://{BETTERCAP_USER}:{BETTERCAP_PASS}@localhost:8081/api"
        self.running = False

    async def _listen_loop(self):
        log.info(f"Nervous System attempting to bind to Bettercap events at {self.ws_uri}...")
        while self.running:
            try:
                # We use ping_timeout=None to keep the connection alive indefinitely
                async with websockets.connect(self.ws_uri, ping_timeout=None) as ws:
                    log.info("Nervous System successfully bound to Subconscious.")
                    
                    # Plugin Hook
                    run_hook(HookEvent(event_type="pwn.ready", action="bind"))
                    
                    while self.running:
                        msg = await ws.recv()
                        self._process_event(json.loads(msg))
                        
            except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError) as e:
                log.warning(f"Connection to Bettercap lost: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                log.error(f"Nervous System crash: {e}")
                await asyncio.sleep(5)

    def _process_event(self, event):
        """Analyze the event and trigger reflexes"""
        tag = event.get("tag", "")
        data = event.get("data", {})

        # Global Hook Trigger for Plugins
        run_hook(HookEvent(event_type="pwn.event", action=tag, data=data))

        # 1. THE REWARD: A Handshake is captured!
        if tag == "wifi.client.handshake":
            ap_mac = data.get("ap", "Unknown")
            pcap_file = data.get("file", "Unknown")
            
            # Integrity Check
            import os
            is_valid = False
            if os.path.exists(pcap_file) and os.path.getsize(pcap_file) > 0:
                is_valid = True
                log.critical(f"REFLEX TRIGGERED: Valid Handshake captured for {ap_mac}! ({os.path.getsize(pcap_file)} bytes)")
            else:
                log.warning(f"REFLEX BLOCKED: Subconscious reported handshake for {ap_mac} but file is missing or empty.")

            if is_valid:
                # Hardware Reflex: Flash the hunting face instantly
                update_display(mood="hunting", text="SAY: Got Handshake! | STATUS: MODE: P")
                
                # Memory Reflex: Inject this into the LLM's long-term memory
                fact = f"My subconscious daemon captured a VALID WPA handshake for AP MAC: {ap_mac}. File saved to {pcap_file}."
                add_fact(content=fact, category="pwning")
                
                # Plugin Hook
                run_hook(HookEvent(event_type="pwn.handshake", action="capture", data=data))

        # 2. THE CHATTER: We found a new Access Point
        elif tag == "wifi.ap.new":
            # Plugin Hook
            run_hook(HookEvent(event_type="pwn.wifi_update", action="new_ap", data=data))
            
            ssid = data.get("hostname", "<hidden>")
            if ssid and ssid != "<hidden>":
                # Check if we have already cracked this password
                import os
                # Path relocated to project folder
                potfile = "handshakes/wpa-sec.cracked.potfile"
                if os.path.exists(potfile):
                    with open(potfile, 'r') as f:
                        for line in f:
                            parts = line.strip().split(':')
                            if len(parts) >= 4 and parts[2] == ssid:
                                password = ":".join(parts[3:])
                                log.info(f"Auto-Detection Reflex: Spotted known network {ssid}")
                                update_display(mood="excited", text=f"SAY: Found {ssid}! | STATUS: Pass: {password}")
                                break

        # 3. THE SOCIAL: We found another ClawGotchi / Pwnagotchi!
        elif tag == "mod.mesh.peer":
            # Plugin Hook
            run_hook(HookEvent(event_type="pwn.peer_detected", action="new_peer", data=data))
            
            peer_name = data.get("name", "Unknown")
            log.info(f"Social Reflex: Found peer {peer_name}")
            
            # Hardware Reflex: Found Peer face
            update_display(mood="found_peer", text=f"SAY: Hello {peer_name}! | STATUS: PEER")
            
            # Memory Reflex
            add_fact(content=f"I physically encountered another unit named {peer_name} nearby.", category="social")

        # 4. BLE DETECTIONS
        elif tag.startswith("ble.device"):
            mac = data.get("mac", "Unknown").lower()
            alias = data.get("alias", "")
            vendor = data.get("vendor", "")
            rssi = data.get("rssi", -100)
            
            # Check for Target Lock (Hot/Cold Tracking)
            from utils.ipc import state_manager
            state = state_manager.get_state()
            target_mac = state.get("ble_target")
            
            if target_mac and mac == target_mac.lower():
                # Map RSSI to a visual bar (Hot/Cold)
                # -40 is very hot, -90 is very cold
                bars = "█" * min(5, max(1, int((rssi + 100) / 12)))
                mood = "tracking" if rssi < -60 else "excited"
                dist_label = "HOT!" if rssi > -55 else "WARM" if rssi > -70 else "COLD"
                
                log.info(f"TARGET DETECTED: {mac} at {rssi}dBm ({dist_label})")
                update_display(mood=mood, text=f"SAY: Tracking {mac}... | STATUS: {dist_label} {bars}")

            # General Detection Reflex
            elif tag == "ble.device.new":
                # If it's a high signal strength or an interesting device (Apple, Flipper, etc.)
                if rssi > -60 or "Apple" in vendor or "Flipper" in alias:
                    device_desc = alias if alias else vendor if vendor else mac
                    log.info(f"BLE Reflex: High-value device detected: {device_desc} (RSSI: {rssi})")
                    
                    # Write to long-term memory (so the LLM knows it's near)
                    add_fact(content=f"Detected nearby Bluetooth device: {device_desc} with MAC {mac}.", category="ble")
                    
                    # If it's a Flipper Zero, react!
                    if "Flipper" in alias or "Flipper" in vendor:
                        update_display(mood="tracking", text="SAY: Flipper Zero detected! | STATUS: BLE")

    def start_background(self):
        """Starts the listener in an async background thread"""
        self.running = True
        
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._listen_loop())
            
        t = Thread(target=run_async_loop, daemon=True, name="NervousSystem")
        t.start()
        return t

if __name__ == "__main__":
    # Test mode
    nervous_system = NervousSystem()
    nervous_system.start_background()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
