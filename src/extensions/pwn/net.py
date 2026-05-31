import subprocess
from sdk.tool_builder import register_tool

@register_tool
def net_scan() -> str:
    """Scan for available Wi-Fi networks that the unit can connect to (Managed Mode)."""
    try:
        # We use the unified gotchi CLI
        result = subprocess.run(["gotchi", "net", "scan"], capture_output=True, text=True, timeout=30)
        return result.stdout if result.stdout else "No networks found or interface busy."
    except Exception as e:
        return f"Network scan error: {e}"

@register_tool
def net_connect(ssid: str, password: str) -> str:
    """Add a new Wi-Fi network and attempt to connect to it."""
    try:
        result = subprocess.run(["gotchi", "net", "add", ssid, password], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return f"Successfully connected to {ssid}!"
        else:
            return f"Failed to connect to {ssid}: {result.stderr or result.stdout}"
    except Exception as e:
        return f"Connection error: {e}"

@register_tool
def net_status() -> str:
    """Check the current network connection status and IP address."""
    try:
        result = subprocess.run(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"], capture_output=True, text=True)
        active = "Not connected"
        for line in result.stdout.splitlines():
            if line.startswith("yes:"):
                active = f"Connected to: {line.split(':')[1]}"
                break
        
        ip_result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
        ip = ip_result.stdout.strip() or "No IP"
        
        return f"📡 Network Status:\n• {active}\n• IP: {ip}"
    except Exception as e:
        return f"Status error: {e}"

@register_tool
def net_list_saved() -> str:
    """List all saved Wi-Fi networks (SSIDs)."""
    try:
        result = subprocess.run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"], capture_output=True, text=True)
        networks = []
        for line in result.stdout.splitlines():
            if line.endswith(":802-11-wireless"):
                networks.append(line.split(':')[0])
        if not networks:
            return "No saved Wi-Fi networks found."
        return "💾 Saved Wi-Fi Networks:\n• " + "\n• ".join(networks)
    except Exception as e:
        return f"List saved networks error: {e}"

@register_tool
def net_forget(ssid: str) -> str:
    """Forget a saved Wi-Fi network by SSID."""
    try:
        result = subprocess.run(["sudo", "nmcli", "connection", "delete", ssid], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return f"Successfully forgot network: {ssid}"
        else:
            return f"Failed to forget network: {result.stderr or result.stdout}"
    except Exception as e:
        return f"Forget network error: {e}"

@register_tool
def net_show_password(ssid: str) -> str:
    """Show the password for a saved Wi-Fi network."""
    try:
        result = subprocess.run(["sudo", "nmcli", "-s", "-g", "802-11-wireless-security.psk", "connection", "show", ssid], capture_output=True, text=True, timeout=15)
        password = result.stdout.strip()
        if result.returncode == 0 and password:
            return f"🔑 Password for {ssid}: {password}"
        else:
            return f"Could not find password for {ssid}. (It may be open, not saved, or misspelled.)"
    except Exception as e:
        return f"Show password error: {e}"
