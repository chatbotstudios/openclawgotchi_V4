import json
import click
from core.cli.utils import output_result, format_header
from extensions.pwn.wifi import pwn_status, pwn_check_cracks as pwn_list_handshakes, pwn_crack as pwn_crack_handshake, pwn_lock_target

@click.group()
def pwn():
    """Full-spectrum Wi-Fi auditing tools."""
    pass

@pwn.command(name="status")
@click.option('--json', 'as_json', is_flag=True, help="Output in JSON format (machine-readable)")
def pwn_status_cmd(as_json):
    """Show current bettercap and sniffing status."""
    res = pwn_status()
    if as_json:
        # Normalise: if res is a dict use it directly, otherwise wrap in status key
        if isinstance(res, dict):
            output_result(res, as_json=True)
        elif isinstance(res, str):
            try:
                output_result(json.loads(res), as_json=True)
            except (json.JSONDecodeError, TypeError):
                output_result({"status": res}, as_json=True)
        else:
            output_result({"status": str(res)}, as_json=True)
    else:
        format_header("Pwn Status")
        click.echo(res)

@pwn.command(name="list")
@click.option('--json', 'as_json', is_flag=True, help="Output in JSON format (machine-readable)")
def pwn_list(as_json):
    """List captured handshakes."""
    result = pwn_list_handshakes()
    if as_json:
        if isinstance(result, (list, dict)):
            output_result(result, as_json=True)
        else:
            output_result({"handshakes": str(result)}, as_json=True)
    else:
        format_header("Captured Handshakes")
        click.echo(result)

@pwn.command(name="crack")
@click.argument('bssid', required=False)
def pwn_crack(bssid):
    """Attempt to crack handshakes."""
    from core.cli.utils import tactical_print
    tactical_print("CRACK", f"Starting job for {bssid or 'all captured'}...")
    click.echo(pwn_crack_handshake(bssid))

@pwn.command(name="lock")
@click.argument('bssid')
def pwn_lock(bssid):
    """Lock onto a specific target BSSID."""
    from core.cli.utils import tactical_print
    tactical_print("TARGET", f"Locking onto {bssid}")
    click.echo(pwn_lock_target(bssid))


@pwn.command(name="qr")
@click.argument('ssid', required=False)
def pwn_qr(ssid):
    """Show QR code for a cracked network."""
    from extensions.pwn.wifi import pwn_show_qr
    click.echo(pwn_show_qr(ssid))
