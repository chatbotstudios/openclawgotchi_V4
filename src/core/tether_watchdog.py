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
            return res.stdout.strip()
        except:
            return ""

    def _attempt_tether(self, mac: str):
        """Perform the wake-and-connect sequence."""
        if not mac:
            return
        
        try:
            log.info(f"🧲 Internet Lost. Pulsing tether to {mac}...")
            # 1. Wake the Bluetooth radio
            subprocess.run(["sudo", "bluetoothctl", "connect", mac], 
                           capture_output=True, timeout=10)
            time.sleep(2)
            
            # 2. Trigger NetworkManager
            subprocess.run(["sudo", "nmcli", "con", "up", "iPhoneHotspot"], 
                           capture_output=True, timeout=15)
        except Exception as e:
            log.warning(f"🧲 Tether attempt failed: {e}")

    def _run(self):
        self.start_time = time.time()
        log.info(f"🧲 Watchdog Burst Mode started ({self.burst_duration}s duration).")
        while self.running:
            has_net = self._has_internet()
            log.debug(f"🧲 Watchdog Pulse: Internet {'ONLINE' if has_net else 'OFFLINE'}")
            
            if not has_net:
                mac = self._get_tether_mac()
                if mac:
                    self._attempt_tether(mac)
                else:
                    log.debug("No 'iPhoneHotspot' profile found. Skipping watchdog pulse.")
            
            # Determine interval based on elapsed time
            elapsed = time.time() - self.start_time
            
            if elapsed >= self.burst_duration:
                log.info("🧲 Watchdog Burst complete. Turning OFF to save power.")
                self.running = False
                break
                
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
