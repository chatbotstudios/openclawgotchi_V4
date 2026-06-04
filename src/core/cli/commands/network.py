import click
from core.cli.utils import output_result, format_header
from core.commands import manage_wifi_interface, manage_ble_adapter, manage_net

@click.group()
def network():
    """Radio and Networking commands."""
    pass

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
