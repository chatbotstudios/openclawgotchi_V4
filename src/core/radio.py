import subprocess
import logging

log = logging.getLogger(__name__)

def manage_wifi_interface(action: str) -> str:
    """Manage Wi-Fi connectivity. Actions: on, off, status, scan."""
    action = action.lower()
    
    if action in ["off", "disable"]:
        subprocess.run(["sudo", "airmon-ng", "check", "kill"], capture_output=True)
        res = subprocess.run(["sudo", "airmon-ng", "start", "wlan0"], capture_output=True, text=True)
        if "monitor mode enabled" in res.stdout.lower() or "monitor mode already enabled" in res.stdout.lower():
            return "Wi-Fi: OFF-GRID (Monitor Mode Active / Tactical Pulse)"
        return f"Wi-Fi: Error entering tactical mode: {res.stderr}"
    
    elif action in ["on", "enable"]:
        subprocess.run(["sudo", "airmon-ng", "stop", "wlan0mon"], capture_output=True)
        subprocess.run(["sudo", "airmon-ng", "stop", "wlan0"], capture_output=True)
        subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"], capture_output=True)
        return "Wi-Fi: ONLINE (Managed Mode / Returning to Base)"
    
    elif action == "status":
        res = subprocess.run(["nmcli", "device", "status"], capture_output=True, text=True)
        return res.stdout if res.stdout else "Unable to fetch Wi-Fi status."
        
    return "Invalid Wi-Fi action."

def manage_ble_adapter(action: str, value: str = None) -> str:
    """Manage Bluetooth adapter state. Actions: on, off, status, scan, broadcast."""
    action = action.lower()
    
    if action == "on":
        subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"], capture_output=True)
        subprocess.run(["sudo", "bluetoothctl", "power", "on"], capture_output=True)
        subprocess.run(["sudo", "hciconfig", "hci0", "up"], capture_output=True)
        return "Bluetooth Adapter: ONLINE"
    elif action == "off":
        subprocess.run(["sudo", "bluetoothctl", "power", "off"], capture_output=True)
        subprocess.run(["sudo", "rfkill", "block", "bluetooth"], capture_output=True)
        subprocess.run(["sudo", "hciconfig", "hci0", "down"], capture_output=True)
        return "Bluetooth Adapter: OFFLINE"
    elif action == "status":
        res = subprocess.run(["hciconfig"], capture_output=True, text=True)
        return res.stdout if res.stdout else "Bluetooth Adapter: UNKNOWN"
    elif action == "scan":
        from extensions.pwn.ble import pwn_ble_scan
        return pwn_ble_scan()
    elif action == "info":
        res = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True)
        return res.stdout if res.stdout else "No BLE info available."
    elif action == "broadcast":
        subprocess.run(["sudo", "hciconfig", "hci0", "pscan"], capture_output=True)
        subprocess.run(["sudo", "hciconfig", "hci0", "leadv"], capture_output=True)
        subprocess.run(["bluetoothctl", "discoverable", "on"], capture_output=True)
        subprocess.run(["bluetoothctl", "pairable", "on"], capture_output=True)
        return "BLE Broadcasting (Beacon) ENABLED. Device is now discoverable and pairable."
    return "Invalid BLE action."

def manage_net(action: str, ssid: str = None, password: str = None) -> str:
    """Manage Network connections. Actions: ping, dns, routes, scan, connect."""
    if action == "ping":
        res = subprocess.run(["ping", "-c", "4", "8.8.8.8"], capture_output=True, text=True)
        return res.stdout
    elif action == "dns":
        res = subprocess.run(["cat", "/etc/resolv.conf"], capture_output=True, text=True)
        return res.stdout
    elif action == "routes":
        res = subprocess.run(["ip", "route"], capture_output=True, text=True)
        return res.stdout
    return "Invalid net action."
