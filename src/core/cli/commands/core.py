import click
import subprocess
from pathlib import Path
from core.cli.utils import output_result, format_header

# Fix path to find src/
PROJECT_DIR = Path(__file__).parent.parent.parent.parent.parent.resolve()

from core.commands import get_status_report, format_status_plain, set_llm_mode, clear_bot_history

@click.command()
@click.option('--json', 'as_json', is_flag=True, help="Output in JSON format")
def status(as_json):
    """Show current hardware and bot status."""
    report = get_status_report()
    if as_json:
        output_result(report, as_json=True)
    else:
        format_header("Gotchi Status")
        click.echo(format_status_plain(report))

@click.command()
@click.argument('mode_name', required=False)
def mode(mode_name):
    """Switch between lite and pro LLM modes."""
    from core.cli.utils import success_print
    _, is_lite = set_llm_mode(mode_name)
    success_print(f"LLM Mode set to: {'Lite (Flash)' if is_lite else 'Pro (Reasoning)'}")

@click.command(name="help")
@click.pass_context
def help_cmd(ctx):
    """Show the professional field manual."""
    format_header("OpenClawGotchi Field Manual")
    click.echo("Usage: gotchi [COMMAND] [ARGS]...")
    click.echo("")
    click.echo("System Commands:")
    click.echo("  status, doctor, logs, restart, dash, mode, ui, clear, list")
    click.echo("")
    click.echo("📡 Pwn & Wireless Auditing:")
    click.echo("  pwn_status, pwn_crack, pwn_check_cracks, pwn_show_qr, pwn_hide_qr,")
    click.echo("  pwn_pause, pwn_lock_target, pwn_whitelist, pwn_system_control,")
    click.echo("  pwn_ble_scan, pwn_ble_track, pwn_ble_purge")
    click.echo("")
    click.echo("🌐 Networking & Tethering:")
    click.echo("  net_scan, net_connect, net_status, tether_scan, tether_pair,")
    click.echo("  tether_up, tether_status, manage_wifi_interface, manage_ble_adapter,")
    click.echo("  manage_net")
    click.echo("")
    click.echo("⏰ Scheduling & Automation:")
    click.echo("  create_reminder, manage_cron, manage_reminders, list_my_cron_jobs,")
    click.echo("  create_recurring_task, delete_cron_job, add_scheduled_task,")
    click.echo("  list_scheduled_tasks, remove_scheduled_task")
    click.echo("")
    click.echo("🧠 Knowledge & Memory:")
    click.echo("  recall_memory, remember_fact, recall_facts, recall_messages,")
    click.echo("  write_daily_log, flush_context")
    click.echo("")
    click.echo("🖼️ Hardware Interface:")
    click.echo("  show_face, add_custom_face")
    click.echo("")
    click.echo("⚙️ System Diagnostics & Administration:")
    click.echo("  execute_bash, run_cli, git_command, manage_service, check_syntax,")
    click.echo("  restart_self, safe_restart, health_check, log_error, log_change,")
    click.echo("  read_architecture")
    click.echo("")
    click.echo("Use 'gotchi [COMMAND] --help' for details on any command.")

@click.command()
@click.option('--full', is_flag=True, help="Run a full diagnostic sweep")
@click.option('--json', 'as_json', is_flag=True, help="Output in JSON format")
def doctor(full, as_json):
    """Full system diagnostic."""
    if not as_json:
        format_header("Gotchi Doctor")
    
    from utils.doctor import main as run_diagnostics
    run_diagnostics()

@click.command()
@click.argument('action', required=False, default='tail')
def logs(action):
    """Stream or manage bot logs. Actions: tail, clear, extended."""
    import shutil
    if not shutil.which("journalctl"):
        click.secho("⚠️  journalctl is not available on this system (Linux-only systemd logger).", fg='bright_yellow', bold=True)
        click.echo("On macOS / local PC deployments, the bot outputs its logs directly to stdout/stderr.")
        click.echo("To view live logs, launch your bot in the foreground via:")
        click.secho("   gotchi run-bot", fg='bright_cyan', bold=True)
        return

    if action == 'tail':
        subprocess.run(["journalctl", "-u", "gotchi", "-n", "50", "-f"])
    elif action == 'clear':
        subprocess.run(["sudo", "journalctl", "--vacuum-time=1s"])
    elif action == 'extended':
        subprocess.run(["journalctl", "-u", "gotchi"])

@click.command()
def restart():
    """Safely restart the Gotchi service."""
    import shutil
    if not shutil.which("systemctl"):
        click.secho("⚠️  systemctl is not available on this system (Linux-only systemd service).", fg='bright_yellow', bold=True)
        click.echo("On macOS / local PC deployments, please restart your bot process in your terminal shell.")
        return
    click.echo("Restarting Gotchi service...")
    subprocess.run(["sudo", "systemctl", "restart", "gotchi"])

@click.command()
@click.option('--refresh-rate', default=2.0, help="Refresh rate in seconds")
def dash(refresh_rate):
    """Launch the live tactical dashboard."""
    from cli.dashboard.main import run_dashboard
    run_dashboard(refresh_rate)

@click.command()
def clear():
    """Clear local history (CLI context)."""
    if click.confirm('Wipe history for CLI?'):
        clear_bot_history(0)
        click.echo("History cleared.")

@click.command(name="list")
def list_tools():
    """List all available AI tools."""
    from core.registry import load_all_extensions, get_registered_tools
    load_all_extensions(str(PROJECT_DIR / "src" / "extensions"))
    tools = get_registered_tools()
    format_header("Available Tools")
    for name in tools.keys():
        click.echo(f"• {name}")

@click.group()
def ui():
    """UI and Display configuration."""
    pass

@ui.command(name="mode")
@click.argument('mode_setting', type=click.Choice(['dark', 'light'], case_sensitive=False))
def ui_mode(mode_setting):
    """Set the e-Paper display mode (dark or light)."""
    from core.commands import set_env_var
    from core.cli.utils import success_print
    new_state = (mode_setting.lower() == 'dark')
    set_env_var("DARK_MODE", "1" if new_state else "0")
    success_print(f"UI Mode set to: {'DARK' if new_state else 'LIGHT'}")
    click.secho("  (Display will update on next refresh)", fg='bright_blue', italic=True)
@click.command()
def run_bot():
    """Internal use: Entrypoint for the systemd service."""
    from main import main
    main()

@click.command()
def setup():
    """Launch the interactive terminal Gotchi Setup Wizard."""
    import subprocess
    wizard_path = PROJECT_DIR / "src" / "cli" / "wizard.mjs"
    try:
        subprocess.run(["node", str(wizard_path)], check=True)
    except subprocess.CalledProcessError:
        click.echo("Setup wizard exited or failed.", err=True)
    except FileNotFoundError:
        click.echo("Error: Node.js is required to run the setup wizard.", err=True)

@click.command()
@click.option('--port', default=8000, help="Localhost port to bind the server")
def serve(port):
    """Launch the localhost live web dashboard server."""
    click.echo(f"Starting localhost live web dashboard on port {port}...")
    from ui.web_dash import ThreadingHTTPServer, WebDashboardHandler
    try:
        server = ThreadingHTTPServer(("0.0.0.0", port), WebDashboardHandler)
        click.secho(f"✓ Dashboard running at http://localhost:{port}", fg='bright_green', bold=True)
        click.echo("Press Ctrl+C to stop the server.")
        server.serve_forever()
    except Exception as e:
        click.echo(f"Error starting web server: {e}", err=True)
