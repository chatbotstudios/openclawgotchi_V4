import requests
import os
import datetime
from requests.auth import HTTPBasicAuth
from sdk.tool_builder import register_tool
from config import BETTERCAP_URL, BETTERCAP_USER, BETTERCAP_PASS

BLE_LOG_DIR = "handshakes/BLE"

def get_auth():
    return HTTPBasicAuth(BETTERCAP_USER, BETTERCAP_PASS)

def _ensure_log_dir():
    os.makedirs(BLE_LOG_DIR, exist_ok=True)

def _log_event(filename: str, content: str):
    _ensure_log_dir()
    filepath = os.path.join(BLE_LOG_DIR, filename)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filepath, "a") as f:
        f.write(f"[{timestamp}]\n{content}\n{'-'*40}\n")

@register_tool
def pwn_ble_scan() -> str:
    """Scan for nearby Bluetooth Low Energy (BLE) devices and return a tactical summary."""
    try:
        url = f"{BETTERCAP_URL}/session"
        r = requests.get(url, auth=get_auth(), timeout=3)
        if r.status_code != 200:
             # Check uptime to see if we're just booting
            try:
                with open('/proc/uptime', 'r') as f:
                    uptime = float(f.readline().split()[0])
                if uptime < 120:
                    return "BLE: [WARMING UP: INITIALIZING ADAPTER...]"
            except:
                pass
            r.raise_for_status()
        
        session = r.json()
        devices = session.get("ble", {}).get("devices", [])
        
        if not devices:
            # Self-healing: Try to force ble.recon on if it seems dead
            try:
                requests.post(f"{BETTERCAP_URL}/session", auth=get_auth(), json={"cmd": "ble.recon on"}, timeout=2)
            except: pass
            return "No BLE devices detected yet. (Sent 'ble.recon on' pulse - try again in 5s)."
            
        # Sort by signal strength
        sorted_devs = sorted(devices, key=lambda x: x.get('rssi', -100), reverse=True)
        
        lines = ["📡 BLE Tactical Scan:"]
        for dev in sorted_devs[:15]:  # Top 15 closest
            mac = dev.get('mac', '??')
            vendor = dev.get('vendor', 'Unknown')
            alias = dev.get('alias', '')
            rssi = dev.get('rssi', -100)
            
            # Distance estimation (rough)
            dist = "Close" if rssi > -60 else "Mid" if rssi > -80 else "Far"
            
            name = alias if alias else vendor
            lines.append(f"• [{rssi}dBm] {name} ({mac}) - {dist}")
            
        output = "\n".join(lines)
        _log_event("scans.log", output)
        return output
    except Exception as e:
        return f"BLE Scan Error: {e}"

@register_tool
def pwn_ble_track(mac_address: str) -> str:
    """Lock onto a specific BLE MAC address for proximity tracking (Hot/Cold)."""
    try:
        from utils.ipc import state_manager
        mac_address = mac_address.strip().lower()
        
        if not mac_address or mac_address == "clear":
            state_manager.update_key("ble_target", None)
            _log_event("tracking.log", "BLE tracking cleared.")
            return "BLE tracking cleared."
            
        state_manager.update_key("ble_target", mac_address)
        _log_event("tracking.log", f"Target Lock: Tracking proximity for {mac_address}...")
        return f"Target Lock: Tracking proximity for {mac_address}..."
    except Exception as e:
        return f"Failed to set BLE track: {e}"

@register_tool
def pwn_ble_purge() -> str:
    """Clear all discovered BLE devices from the current session to reset the environment."""
    try:
        url = f"{BETTERCAP_URL}/session"
        payload = {"cmd": "ble.clear"}
        requests.post(url, auth=get_auth(), json=payload, timeout=3)
        _log_event("tracking.log", "BLE session purged. Starting fresh recon...")
        return "BLE session purged. Starting fresh recon..."
    except Exception as e:
        return f"Purge failed: {e}"
