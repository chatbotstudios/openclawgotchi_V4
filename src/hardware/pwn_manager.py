import logging
import secrets
import string
import subprocess
import time
from pathlib import Path

log = logging.getLogger("PwnManager")

class PwnManager:
    def __init__(self):
        self.bettercap_proc = None
        self.pwn_daemon = None
        self.nervous_system = None
        self._api_user = None
        self._api_pass = None

    def _get_api_creds(self):
        """Get Bettercap API credentials from .env, generating a random password if unset."""
        if self._api_user and self._api_pass:
            return self._api_user, self._api_pass
        try:
            import os

            from dotenv import load_dotenv
            load_dotenv()
            user = os.getenv("BETTERCAP_API_USER", "gotchi")
            pw = os.getenv("BETTERCAP_API_PASS", "")
            if not pw:
                pw = ''.join(secrets.choice(string.hexdigits) for _ in range(32))
            self._api_user = user
            self._api_pass = pw
            return user, pw
        except Exception:
            return "gotchi", ''.join(secrets.choice(string.hexdigits) for _ in range(32))

    def wait_for_interface(self, iface="wlan0mon", timeout=15):
        """Wait for monitor interface to appear"""
        from config import MOCK_HARDWARE
        if MOCK_HARDWARE:
            return True
        for _ in range(timeout):
            if subprocess.run(["ip", "link", "show", iface], capture_output=True).returncode == 0:
                return True
            time.sleep(1)
        return False

    def _wait_for_bettercap_api(self, timeout=10):
        """Poll REST API until ready"""
        import requests
        from requests.auth import HTTPBasicAuth
        api_user, api_pass = self._get_api_creds()
        for _ in range(timeout * 2):  # 0.5s ticks
            try:
                # Use credentials from .env
                res = requests.get("http://127.0.0.1:8081/api/session", 
                                   auth=HTTPBasicAuth(api_user, api_pass), 
                                   timeout=1)
                if res.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(0.5)
        return False

    def start(self, hunt_on_boot=True):
        from config import MOCK_HARDWARE
        if MOCK_HARDWARE:
            log.info("MOCK_HARDWARE=1: Skipping Bettercap/radio subsystem.")
            return True
        try:
            if not hunt_on_boot:
                log.info("HUNT_ON_BOOT is false, skipping daemon start.")
                return True
                
            log.info("Starting Pwnagotchi Subconscious...")
                
            # 1. Ensure clean state
            subprocess.run(["sudo", "pkill", "-9", "bettercap"], capture_output=True, check=False)
            
            # 2. Switch to monitor mode (use CLI for consistency)
            try:
                subprocess.run(["gotchi", "wifi", "on"], capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                log.error(f"Failed to bring up wifi via gotchi CLI: {e}")
                # Attempt manual fallback just in case CLI fails
                subprocess.run(["sudo", "airmon-ng", "start", "wlan0"], capture_output=True, check=False)

            if not self.wait_for_interface(timeout=20):
                log.error("wlan0mon never appeared. Bettercap will fail.")
                return False
            
            # 3. Start Bettercap with proper logging + health check
            # Find the project root from this file's location (src/hardware/pwn_manager.py -> project_root)
            project_root = Path(__file__).resolve().parent.parent.parent
            handshake_path = str(project_root / "handshakes")
            Path(handshake_path).mkdir(exist_ok=True)
            
            api_user, api_pass = self._get_api_creds()
            
            cmd = [
                "sudo", "bettercap", "-iface", "wlan0mon",
                "-eval", f"set api.rest.user {api_user}; set api.rest.pass {api_pass}; "
                         f"api.rest on; ble.recon on; wifi.recon on; "
                         f"set wifi.handshakes.path {handshake_path}"
            ]
            
            self.bettercap_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 4. Wait for REST API
            if not self._wait_for_bettercap_api(timeout=10):
                log.warning("Bettercap started but REST API is not responding. Daemons may crash.")
            else:
                log.info("Bettercap API is online.")
                
            # 5. Start Python layers
            from .bettercap_listener import NervousSystem
            from .subconscious_pwn import PwnDaemon
            
            self.pwn_daemon = PwnDaemon()
            self.nervous_system = NervousSystem()
            
            self.pwn_daemon.start_background()
            self.nervous_system.start_background()
            
            log.info("✅ Full Pwnagotchi Subconscious stack started successfully")
            return True
            
        except Exception as e:
            log.error(f"Failed to start Pwn system: {e}")
            return False
