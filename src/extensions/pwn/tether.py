import subprocess
import time
import logging
from sdk.tool_builder import register_tool

log = logging.getLogger(__name__)

@register_tool
def tether_scan() -> str:
    """Scan for nearby Bluetooth devices specifically to find a tethering host."""
    print("📡 Scanning for Bluetooth targets (5s)...")
    try:
        # Use hcitool/bluetoothctl to scan
        cmd = "sudo bluetoothctl --timeout 5 scan on"
        proc = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=8)
        
        # Get paired/known devices too
        known = subprocess.run(["sudo", "bluetoothctl", "devices"], capture_output=True, text=True, timeout=5).stdout
        
        return f"Nearby/Known Devices:\n{known}\n\nScan Result:\n{proc.stdout}"
    except Exception as e:
        return f"Scan failed: {e}"

@register_tool
def tether_pair(mac: str) -> str:
    """Orchestrate a trusted pairing bond with a mobile device."""
    print(f"🤝 Initiating bond with {mac}...")
    try:
        # We use a heredoc style to talk to bluetoothctl
        cmds = f"power on\nagent on\ndefault-agent\npair {mac}\ntrust {mac}\nexit\n"
        proc = subprocess.run(["sudo", "bluetoothctl"], input=cmds, capture_output=True, text=True, timeout=15)
        
        if "Pairing successful" in proc.stdout or "already paired" in proc.stdout.lower():
            return f"✅ Bond Established with {mac}. You can now run 'gotchi tether up'."
        return f"❌ Pairing might have failed. Output:\n{proc.stdout}"
    except Exception as e:
        return f"Pairing Error: {e}"

@register_tool
def tether_up(mac: str) -> str:
    """Create a PANU network profile and bring the Bluetooth internet tunnel online."""
    print(f"🌐 Bringing up Tether tunnel to {mac}...")
    try:
        # Check if already up
        check_ip = subprocess.run(["ip", "addr", "show", "bnep0"], capture_output=True, text=True, timeout=5)
        if check_ip.returncode == 0 and "inet " in check_ip.stdout:
            return "✅ Tether is ALREADY ONLINE. No action needed."

        # 1. Clean up old profiles if they exist (to avoid 'suitability' errors on re-pairing)
        # We only delete if not currently active to avoid breaking existing links
        subprocess.run(["sudo", "nmcli", "connection", "delete", "iPhoneHotspot"], capture_output=True, timeout=15)
        
        # 2. Wake up the device connection first
        log.info(f"Connecting Bluetooth to {mac}...")
        subprocess.run(["sudo", "bluetoothctl", "connect", mac], capture_output=True, timeout=15)
        time.sleep(2)
        
        # 3. Create the flexible PANU profile
        add_cmd = [
            "sudo", "nmcli", "connection", "add", 
            "type", "bluetooth", 
            "con-name", "iPhoneHotspot", 
            "bluetooth.type", "panu", 
            "bluetooth.bdaddr", mac
        ]
        subprocess.run(add_cmd, capture_output=True, text=True, timeout=15)
        
        # 4. Activation
        log.info("Activating NetworkManager connection...")
        up_proc = subprocess.run(["sudo", "nmcli", "con", "up", "iPhoneHotspot"], capture_output=True, text=True, timeout=20)
        
        if "successfully activated" in up_proc.stdout:
            # Check for IP
            ip_check = subprocess.run(["ip", "addr", "show", "bnep0"], capture_output=True, text=True, timeout=15).stdout
            return f"🚀 Tether Active!\n{ip_check}"
        else:
            return f"❌ Activation failed. Ensure iPhone Hotspot screen is OPEN.\nError: {up_proc.stderr or up_proc.stdout}"
            
    except Exception as e:
        return f"Tether Error: {e}"

@register_tool
def tether_status() -> str:
    """Check the current state of the Bluetooth tethering tunnel."""
    try:
        res = subprocess.run(["ip", "addr", "show", "bnep0"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            return f"✅ Tether ONLINE:\n{res.stdout}"
        return "❌ Tether OFFLINE (bnep0 interface not found)."
    except:
        return "❌ Tether OFFLINE."
