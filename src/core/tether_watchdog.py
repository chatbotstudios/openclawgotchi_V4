import subprocess
import time
import threading
import logging

log = logging.getLogger("TetherWatchdog")

class TetherWatchdog:
    """
    Background watchdog that ensures the bot stays connected to the iPhone tether.
    """
    def __init__(self, interval_burst=30, interval_steady=300, burst_duration=300):
        self.interval_burst = interval_burst
        self.interval_steady = interval_steady
        self.burst_duration = burst_duration
        self.running = False
        self.start_time = 0
        self._thread = None

    def _has_internet(self) -> bool:
        """Check if we have a working internet connection."""
        try:
            # Ping Google DNS with a short timeout
            subprocess.run(["ping", "-c", "1", "-W", "2", "8.8.8.8"], 
                           capture_output=True, check=True, timeout=3)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
        except Exception as e:
            log.debug(f"Watchdog: Internet check failed: {e}")
            return False

    def _get_tether_mac(self) -> str:
        """Extract the paired iPhone MAC from the NetworkManager profile."""
        try:
            cmd = "sudo nmcli -g bluetooth.bdaddr connection show iPhoneHotspot"
            res = subprocess.run(cmd.split(), capture_output=True, text=True)
            return res.stdout.strip().replace("\\", "")
        except:
            return ""

    def _is_tether_active(self) -> bool:
        """Check if the iPhoneHotspot is currently active in NetworkManager."""
        try:
            res = subprocess.run(["nmcli", "-t", "-f", "NAME,STATE", "con", "show", "--active"], capture_output=True, text=True)
            return "iPhoneHotspot:activated" in res.stdout
        except:
            return False

    def _keepalive_ping(self, mac: str):
        """Send packets over BNEP and Bluetooth Link Layer to prevent iOS idle drop."""
        try:
            # 1. IP-level ping to the hardcoded iPhone Personal Hotspot gateway
            subprocess.run(["ping", "-c", "1", "172.20.10.1"], capture_output=True, timeout=2)
            # 2. Link-layer ping to keep the Bluetooth radio alive
            if mac:
                subprocess.run(["sudo", "l2ping", "-c", "1", mac], capture_output=True, timeout=2)
        except:
            pass

    def _attempt_tether(self, mac: str):
        """Perform the wake-and-connect sequence."""
        if not mac:
            return
        
        try:
            log.info(f"🧲 Tether Watchdog: [1/4] Scanning for Bluetooth PAN tether at {mac}...")
            
            # Clean slate: nuke any stuck connections
            subprocess.run(["sudo", "nmcli", "con", "down", "iPhoneHotspot"], capture_output=True)
            subprocess.run(["sudo", "bluetoothctl", "disconnect", mac], capture_output=True)
            
            # Ensure adapter is ON
            subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"], capture_output=True)
            subprocess.run(["sudo", "bluetoothctl", "power", "on"], capture_output=True)
            subprocess.run(["sudo", "hciconfig", "hci0", "up"], capture_output=True)
            
            # 1. Wake the Bluetooth radio
            log.info(f"🧲 Tether Watchdog: [2/4] Found target! Pairing & Connecting to MAC {mac}...")
            try:
                subprocess.run(["sudo", "bluetoothctl", "connect", mac], 
                               capture_output=True, timeout=25)
            except subprocess.TimeoutExpired:
                log.warning("🧲 Tether Watchdog: bluetoothctl connect timed out, but continuing to nmcli...")
            time.sleep(2)
            
            # 2. Trigger NetworkManager
            log.info("🧲 Tether Watchdog: [3/4] Bringing up NetworkManager profile 'iPhoneHotspot'...")
            subprocess.run(["sudo", "nmcli", "con", "up", "iPhoneHotspot"], 
                           capture_output=True, timeout=15)
                           
            log.info("🧲 Tether Watchdog: [4/4] Tethering sequence complete! Dual Uplink is ACTIVE.")
        except Exception as e:
            log.warning(f"🧲 Tether Watchdog: Tether attempt failed: {e}")

    def _run(self):
        self.start_time = time.time()
        log.info(f"🧲 Watchdog Burst Mode started ({self.burst_duration}s duration).")
        
        # Initial Boot/Burst sequence: Always attempt to establish the Dual Uplink
        mac = self._get_tether_mac()
        if mac:
            log.info("🧲 Establishing Dual Uplink (Hitless Transition) on boot...")
            self._attempt_tether(mac)
            
        while self.running:
            is_active = self._is_tether_active()
            has_net = self._has_internet()
            
            log.debug(f"🧲 Watchdog Pulse: Tether={'ACTIVE' if is_active else 'DROPPED'} | Internet={'ONLINE' if has_net else 'OFFLINE'}")
            
            if not is_active:
                if mac:
                    log.warning("🧲 Tether dropped or missing! Re-establishing Dual Uplink...")
                    self._attempt_tether(mac)
                else:
                    log.debug("No 'iPhoneHotspot' profile found. Skipping watchdog pulse.")
            else:
                self._keepalive_ping(mac)
            
            # Determine interval based on elapsed time
            elapsed = time.time() - self.start_time
            
            if elapsed >= self.burst_duration:
                current_interval = self.interval_steady
            else:
                current_interval = self.interval_burst
            
            # Sleep in small increments to allow for faster shutdown
            for _ in range(int(current_interval)):
                if not self.running: break
                time.sleep(1)
        
        self.running = False

    def restart_burst(self):
        """Restart the watchdog for a fresh burst."""
        self.stop()
        time.sleep(1)
        self.start()

    def start(self):
        if self.running: return
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        log.info("Tether Watchdog ACTIVE (Magnetic Mode).")

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
        log.info("Tether Watchdog STOPPED.")

# Global instance
watchdog = TetherWatchdog()
