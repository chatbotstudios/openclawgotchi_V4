import subprocess
import time
import threading
import logging

log = logging.getLogger("TetherWatchdog")

class TetherWatchdog:
    """
    Background watchdog that ensures the bot stays connected to the iPhone tether.
    """
    def __init__(self, interval_burst=30, interval_steady=120, burst_duration=300):
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
            res = subprocess.run(["nmcli", "-t", "-f", "NAME,STATE", "con", "show", "--active"], capture_output=True, text=True, timeout=5)
            if "iPhoneHotspot:activated" not in res.stdout:
                return False
            
            # Strict validation: Check that bnep0 actually has a valid IP address
            ip_res = subprocess.run(["ip", "-4", "addr", "show", "dev", "bnep0"], capture_output=True, text=True)
            if "inet " not in ip_res.stdout or "169.254." in ip_res.stdout:
                return False
                
            return True
        except:
            return False

    def _keepalive_ping(self, mac: str):
        """Send packets over BNEP to prevent iOS idle drop."""
        try:
            # 1. IP-level ping to the hardcoded iPhone Personal Hotspot gateway
            subprocess.run(["ping", "-c", "1", "172.20.10.1"], capture_output=True, timeout=2)
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
            time.sleep(3)
            
            # Ensure adapter is ON and Discoverable
            subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"], capture_output=True)
            subprocess.run(["sudo", "bluetoothctl", "power", "on"], capture_output=True)
            subprocess.run(["sudo", "hciconfig", "hci0", "up"], capture_output=True)
            subprocess.run(["sudo", "bluetoothctl", "discoverable", "on"], capture_output=True)
            
            # 1. Wake the Bluetooth radio
            log.info(f"🧲 Tether Watchdog: [2/4] Found target! Pairing & Connecting to MAC {mac}...")
            try:
                subprocess.run(["sudo", "bluetoothctl", "connect", mac], 
                               capture_output=True, timeout=25)
            except subprocess.TimeoutExpired:
                log.warning("🧲 Tether Watchdog: bluetoothctl connect timed out, but continuing...")
                
            # Poll for bnep0 to spawn from the bluetoothctl connect
            bnep_spawned = False
            for _ in range(5):
                link_res = subprocess.run(["ip", "link", "show", "bnep0"], capture_output=True)
                if link_res.returncode == 0:
                    bnep_spawned = True
                    break
                time.sleep(2)
                
            if not bnep_spawned:
                log.warning("🧲 Tether Watchdog: bnep0 interface did not spawn! Target might be asleep or blocking the connection.")
                return
            
            # 2. Trigger NetworkManager
            log.info("🧲 Tether Watchdog: [3/4] Bringing up NetworkManager profile 'iPhoneHotspot'...")
            res = subprocess.run(["sudo", "nmcli", "con", "up", "iPhoneHotspot"], 
                           capture_output=True, timeout=15)
            
            if res.returncode != 0:
                err_msg = res.stderr.decode('utf-8').strip() if res.stderr else "Unknown error"
                log.warning(f"🧲 Tether Watchdog: nmcli connection failed. Output: {err_msg}")
                return
                
            time.sleep(1) # Give kernel time to spawn bnep0
            
            # Verify bnep0 actually exists and received an IP address
            # Poll for up to 10 seconds to allow DHCP to assign an IP
            valid_ip = False
            for _ in range(5):
                link_res = subprocess.run(["ip", "link", "show", "bnep0"], capture_output=True)
                if link_res.returncode == 0:
                    ip_res = subprocess.run(["ip", "-4", "addr", "show", "dev", "bnep0"], capture_output=True, text=True)
                    if "inet " in ip_res.stdout and "169.254." not in ip_res.stdout:
                        valid_ip = True
                        log.debug(f"🧲 Tether Watchdog: bnep0 IP output: {ip_res.stdout.strip()}")
                        break
                time.sleep(2)
                
            if not valid_ip:
                log.warning("🧲 Tether Watchdog: bnep0 did not receive a valid IP within 10s! Hotspot is offline or DHCP failed.")
                subprocess.run(["sudo", "nmcli", "con", "down", "iPhoneHotspot"], capture_output=True)
                return
                
            # Verify NetworkManager actually considers it fully activated
            if not self._is_tether_active():
                log.warning("🧲 Tether Watchdog: NetworkManager profile is not in 'activated' state. Sequence failed.")
                return
                           
            # 3. MTU Throttle & Traffic Control (Prevent firmware panic & brownout)
            log.info("🧲 Tether Watchdog: Applying MTU throttle and traffic control pacing (250kbps) to bnep0...")
            subprocess.run(["sudo", "ip", "link", "set", "dev", "bnep0", "mtu", "900"], capture_output=True)
            subprocess.run(["sudo", "tc", "qdisc", "replace", "dev", "bnep0", "root", "tbf", "rate", "250kbit", "burst", "10kb", "latency", "50ms"], capture_output=True)
                           
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
                # Detect crash edge-case and dump forensics
                if getattr(self, '_was_active', False):
                    log.error("🧲 TETHER CRASH DETECTED! Executing hardware forensics dump...")
                    try:
                        from utils.forensics import get_forensics_logger, dump_kernel_dmesg
                        get_forensics_logger().error("--- [TETHER CRASH DETECTED] ---")
                        dump_kernel_dmesg()
                    except Exception:
                        pass
                self._was_active = False
                
                self.net_fails = 0
                if mac:
                    log.warning("🧲 Tether dropped or missing! Re-establishing Dual Uplink...")
                    self._attempt_tether(mac)
                else:
                    log.debug("No 'iPhoneHotspot' profile found. Skipping watchdog pulse.")
            elif not has_net:
                self.net_fails = getattr(self, 'net_fails', 0) + 1
                if self.net_fails >= 3:
                    if mac:
                        log.warning("🧲 No internet for 3 consecutive pulses! Bouncing tether...")
                        self._attempt_tether(mac)
                    self.net_fails = 0
                else:
                    log.debug(f"🧲 Internet unreachable (Fail {self.net_fails}/3). Waiting for routing table to settle...")
                    self._keepalive_ping(mac)
            else:
                self._was_active = True
                self.net_fails = 0
                self._keepalive_ping(mac)
            
            # Determine interval based on elapsed time
            elapsed = time.time() - self.start_time
            
            if elapsed >= self.burst_duration:
                log.info(f"🧲 Watchdog Burst Mode ({self.burst_duration}s) complete. Shutting down tether watchdog.")
                break
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
