import click
from core.cli.utils import output_result, format_header
from core.commands import manage_wifi_interface, manage_ble_adapter, manage_net

@click.group()
def network():
    """Radio and Networking commands."""
    pass

@network.command(name="status")
def network_status():
    """Display Dual Uplink Network Status."""
    import subprocess
    from core.cli.utils import format_header
    
    # Get wlan0 IP
    try:
        wlan0_res = subprocess.run(["ip", "-4", "addr", "show", "wlan0"], capture_output=True, text=True)
        wlan0_ip = None
        for line in wlan0_res.stdout.split('\\n'):
            if "inet " in line:
                wlan0_ip = line.split()[1].split('/')[0]
                break
    except:
        wlan0_ip = None
        
    # Get bnep0 IP
    try:
        bnep0_res = subprocess.run(["ip", "-4", "addr", "show", "bnep0"], capture_output=True, text=True)
        bnep0_ip = None
        for line in bnep0_res.stdout.split('\\n'):
            if "inet " in line:
                bnep0_ip = line.split()[1].split('/')[0]
                break
    except:
        bnep0_ip = None
        
    # Get SSID
    try:
        ssid_res = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True)
        ssid = ssid_res.stdout.strip()
        if not ssid:
            ssid = "Unknown"
    except:
        ssid = "Unknown"
        
    format_header("CONNECTION STATUS — DUAL UPLINK")
    
    wlan0_status = f"{ssid}\\n→ {wlan0_ip} ✅" if wlan0_ip else "OFFLINE ❌"
    bnep0_status = f"bnep0 (iPhone Hotspot)\\n→ {bnep0_ip} ✅" if bnep0_ip else "OFFLINE ❌"
    
    click.echo(f"📶 Wi-Fi:  {wlan0_status}")
    click.echo(f"📱 BLE Tether:  {bnep0_status}")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    if wlan0_ip and bnep0_ip:
        click.echo("\\nDual uplink active, Commander!")
        click.echo("Both pipes are live. Wi-Fi's handling primary traffic, BLE tether's standing by as redundant uplink.")
    elif wlan0_ip:
        click.echo("\\nWi-Fi is active. BLE Tether is offline.")
    elif bnep0_ip:
        click.echo("\\nBLE Tether is active. Wi-Fi is offline or in hunting mode.")
    else:
        click.echo("\\nALL SYSTEMS OFFLINE.")

@network.group()
def wifi():
    """Wi-Fi radio management."""
    pass

@wifi.command(name="status")
@click.option('--json', 'as_json', is_flag=True)
def wifi_status(as_json):
    """Check Wi-Fi interface status."""
    res = manage_wifi_interface('status')
    output_result(res, as_json)

@wifi.command(name="on")
def wifi_on():
    """Enable Wi-Fi (Managed Mode)."""
    click.echo(manage_wifi_interface('on'))

@wifi.command(name="off")
def wifi_off():
    """Disable Wi-Fi (Monitor/Tactical Mode)."""
    click.echo(manage_wifi_interface('off'))

@wifi.command(name="scan")
def wifi_scan():
    """Scan for nearby Wi-Fi networks."""
    format_header("Nearby Networks")
    click.echo(manage_wifi_interface('scan'))

@network.group()
def ble():
    """Bluetooth hardware controls."""
    pass

@ble.command(name="on")
def ble_on():
    """Enable Bluetooth radio."""
    click.echo(manage_ble_adapter('on'))

@ble.command(name="off")
def ble_off():
    """Disable Bluetooth radio."""
    click.echo(manage_ble_adapter('off'))

@ble.command(name="scan")
def ble_scan():
    """Scan for BLE devices."""
    format_header("BLE Scan Results")
    click.echo(manage_ble_adapter('scan'))

@network.group()
def tether():
    """Bluetooth PAN Tethering."""
    pass

@tether.command(name="burst")
@click.option('--duration', default=300, type=int, help="Duration in seconds for aggressive polling.")
def tether_burst(duration):
    """Start aggressive tether watchdog."""
    from core.tether_watchdog import watchdog
    watchdog.burst_duration = duration
    watchdog.restart_burst()
    click.echo(f"🧲 Tether Burst Mode started ({duration}s).")

@tether.command(name="pair")
@click.argument('mac')
def tether_pair(mac):
    """Pair and trust a Bluetooth tethering device."""
    import subprocess
    click.echo(f"🧲 Launching pairing agent for {mac}...")
    click.echo("⚠️ If a PIN appears, type 'yes' and hit Enter, then tap 'Pair' on your phone.")
    
    try:
        subprocess.run(["sudo", "bluetoothctl", "pair", mac])
        click.echo(f"🧲 Trusting {mac}...")
        subprocess.run(["sudo", "bluetoothctl", "trust", mac])
        click.echo("✅ Pairing sequence complete. Run 'gotchi network tether up' to connect.")
    except Exception as e:
        click.echo(f"❌ Error during pairing: {e}")

@tether.command(name="up")
@click.option('--mac', default=None, help="MAC address of the phone.")
def tether_up(mac):
    """Bring up the Bluetooth PAN tethering tunnel."""
    import subprocess
    import time
    from config import load_env
    
    target_mac = mac
    if not target_mac:
        # Try to pull from .env
        env = load_env()
        target_mac = env.get("BLE_ADDRESS")
        
    if not target_mac:
        # Try to pull from existing NM profile
        try:
            res = subprocess.run(["nmcli", "-g", "bluetooth.bdaddr", "connection", "show", "iPhoneHotspot"], capture_output=True, text=True)
            target_mac = res.stdout.strip().replace("\\", "")
        except:
            pass
            
    if not target_mac:
        click.echo("❌ Error: No MAC address provided and BLE_ADDRESS not set in .env")
        return
        
    click.echo(f"🧲 Waking up {target_mac}...")
    subprocess.run(["sudo", "bluetoothctl", "connect", target_mac], capture_output=True)
    time.sleep(2)
    
    click.echo("🧲 Bringing up NetworkManager profile 'iPhoneHotspot'...")
    res = subprocess.run(["sudo", "nmcli", "connection", "up", "iPhoneHotspot"], capture_output=True, text=True)
    
    if res.returncode == 0:
        click.echo("✅ Tethering tunnel established!")
    else:
        if "unknown connection" in res.stderr.lower():
            click.echo("⚠️ Profile not found. Creating 'iPhoneHotspot' NetworkManager profile...")
            subprocess.run(["sudo", "nmcli", "connection", "add", "type", "bluetooth", "ifname", "*", "con-name", "iPhoneHotspot", "bluetooth.bdaddr", target_mac, "bluetooth.type", "panu"])
            subprocess.run(["sudo", "nmcli", "connection", "up", "iPhoneHotspot"])
            click.echo("✅ Profile created and tunnel established!")
        else:
            click.echo(f"❌ Failed to bring up tunnel: {res.stderr}")

@network.command(name="hunt")
@click.option('--duration', default=900, type=int, help="Duration of offline hunt in seconds (default 900 / 15m).")
@click.option('--mission', default="handshake_hunter_v1", type=str, help="Associated mission ID.")
def network_hunt(duration, mission):
    """Go offline, turn wlan0 to monitor mode, invert UI, and hunt."""
    import subprocess
    import sys
    click.echo(f"📡 Transitioning to Offline Hunt for {duration // 60} minutes...")
    
    # Run the offline hunter in a background python process to prevent blocking the terminal/LLM
    cmd = [
        sys.executable, "-c",
        f"from core.offline_hunter import offline_hunter; offline_hunter.run_hunt({duration}, '{mission}')"
    ]
    
    # Run completely detached from the caller
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    click.echo("🚀 Hunt launched in background. Connection will drop shortly.")

@network.group()
def net():
    """Global network diagnostics."""
    pass

@net.command(name="ping")
def net_ping():
    """Ping test to 8.8.8.8."""
    click.echo(manage_net('ping'))
