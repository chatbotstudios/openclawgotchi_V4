import subprocess
from pathlib import Path

import click

from core.cli.utils import format_header, output_result

# Fix path to find src/
PROJECT_DIR = Path(__file__).parent.parent.parent.parent.parent.resolve()

from core.commands import (
    clear_bot_history,
    format_status_plain,
    get_status_report,
    set_llm_mode,
)


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
def backup():
    """Run the headless backup protocol to sync the bot's brain to the gotchi branch."""
    import subprocess
    format_header("Autonomous Brain Backup")
    backup_script = PROJECT_DIR / "backup_brain.sh"
    if not backup_script.exists():
        click.echo("Error: backup_brain.sh not found at project root.", err=True)
        return
        
    try:
        # Run the script and stream output to console
        process = subprocess.Popen([str(backup_script)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            click.echo(line.strip())
        process.wait()
        if process.returncode != 0:
            click.echo(f"Backup failed with exit code {process.returncode}.", err=True)
    except Exception as e:
        click.echo(f"Failed to execute backup script: {e}", err=True)

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
@click.option('-w', '--watch', type=int, default=0, metavar='N', help="Watch mode: refresh every N seconds")
def doctor(full, as_json, watch):
    """Full system diagnostic."""
    if not as_json:
        format_header("Gotchi Doctor")
    
    from utils.doctor import main as run_diagnostics
    # Pass CLI flags as sys.argv so doctor.main() can read them
    import sys as _sys
    if as_json and '--json' not in _sys.argv:
        _sys.argv.append('--json')
    if watch:
        if '--watch' not in _sys.argv:
            _sys.argv.extend(['--watch', str(watch)])
    run_diagnostics()


@click.command()
@click.option('-o', '--output', default=None, help="Output path for export zip (default: project root)")
def export(output):
    """Create a full backup of bot state: DB, workspace, handshakes, config."""
    import zipfile, datetime
    from config import DB_PATH
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"gotchi-backup-{timestamp}.zip"
    output_path = Path(output) if output else PROJECT_DIR / backup_name
    
    click.echo(f"📦 Creating backup: {output_path}")
    
    # Files/dirs to include
    paths = {
        ".env": PROJECT_DIR / ".env",
        "gotchi.db": DB_PATH,
        "workspace": PROJECT_DIR / "workspace",
        "handshakes": PROJECT_DIR / "handshakes",
        "data": PROJECT_DIR / "data",
        "agents/skills": PROJECT_DIR / "agents" / "skills",
    }
    
    # Exclude patterns
    exclude_dirs = {"__pycache__", ".venv", "venv", "node_modules", ".git", ".pytest_cache"}
    exclude_exts = {".pyc", ".pyo"}
    
    added = 0
    skipped = 0
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for arcname, src in paths.items():
            if not src.exists():
                click.echo(f"  ⚠️  Skipping {arcname} (not found)")
                skipped += 1
                continue
            
            if src.is_file():
                zf.write(src, arcname)
                added += 1
            elif src.is_dir():
                for file_path in src.rglob("*"):
                    # Skip excluded dirs
                    if any(p in file_path.parts for p in exclude_dirs):
                        continue
                    if file_path.suffix in exclude_exts:
                        continue
                    if file_path.is_file():
                        zf.write(file_path, f"{arcname}/{file_path.relative_to(src)}")
                        added += 1
    
    size_mb = output_path.stat().st_size / (1024 * 1024)
    click.echo(f"  ✅ Backup complete: {added} files ({size_mb:.1f} MB)")
    click.echo(f"  📍 {output_path}")
    if skipped:
        click.echo(f"  ⚠️  {skipped} item(s) skipped (not found)")


@click.command()
@click.option('--older-than', type=int, default=0, metavar='DAYS', help="Delete messages older than N days")
@click.option('--keep-last', type=int, default=0, metavar='N', help="Keep only the last N messages per user")
@click.option('--handshakes', 'clean_handshakes', type=int, default=0, metavar='DAYS', help="Delete handshake PCAPs older than N days")
@click.option('--dry-run', is_flag=True, help="Show what would be deleted without deleting")
@click.option('--all', 'clean_all', is_flag=True, help="Delete all messages and pending tasks")
def db_clean(older_than, keep_last, clean_handshakes, dry_run, clean_all):
    """Clean up old database records and handshake files to save space."""
    import sqlite3, datetime, glob
    
    from config import DB_PATH, PROJECT_DIR
    
    total_freed = 0
    
    if clean_all:
        click.echo("🧹 Full database cleanup requested...")
    
    # ── Messages cleanup ──
    if older_than > 0 or clean_all:
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cutoff = (datetime.datetime.now() - datetime.timedelta(days=older_than)).isoformat() if older_than > 0 else "1970-01-01"
            
            if clean_all:
                count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
                if dry_run:
                    click.echo(f"  [DRY RUN] Would delete all {count} messages")
                else:
                    conn.execute("DELETE FROM messages")
                    conn.commit()
                    click.echo(f"  🗑️  Deleted all {count} messages")
                    total_freed += count
            elif older_than > 0:
                count = conn.execute("SELECT COUNT(*) FROM messages WHERE timestamp < ?", (cutoff,)).fetchone()[0]
                if dry_run:
                    click.echo(f"  [DRY RUN] Would delete {count} messages older than {older_than} days")
                else:
                    conn.execute("DELETE FROM messages WHERE timestamp < ?", (cutoff,))
                    conn.commit()
                    click.echo(f"  🗑️  Deleted {count} messages older than {older_than} days")
                    total_freed += count
            conn.close()
        except Exception as e:
            click.echo(f"  ❌ Messages cleanup failed: {e}")
    
    # ── Keep-last messages ──
    if keep_last > 0:
        try:
            conn = sqlite3.connect(str(DB_PATH))
            # Get all distinct user_ids
            user_ids = conn.execute("SELECT DISTINCT user_id FROM messages").fetchall()
            deleted_total = 0
            for (uid,) in user_ids:
                # Count total for this user
                total = conn.execute("SELECT COUNT(*) FROM messages WHERE user_id = ?", (uid,)).fetchone()[0]
                if total > keep_last:
                    # Get the ID of the Nth from last message to keep
                    keep_from = conn.execute(
                        "SELECT id FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT 1 OFFSET ?",
                        (uid, keep_last - 1)
                    ).fetchone()
                    if keep_from:
                        to_delete = conn.execute(
                            "SELECT COUNT(*) FROM messages WHERE user_id = ? AND id < ?",
                            (uid, keep_from[0])
                        ).fetchone()[0]
                        if dry_run:
                            click.echo(f"  [DRY RUN] Would delete {to_delete} old messages for user {uid} (keeping last {keep_last})")
                        else:
                            conn.execute("DELETE FROM messages WHERE user_id = ? AND id < ?", (uid, keep_from[0]))
                            deleted_total += to_delete
            if not dry_run and deleted_total:
                conn.commit()
                click.echo(f"  🗑️  Trimmed {deleted_total} old messages (keeping last {keep_last} per user)")
                total_freed += deleted_total
            conn.close()
        except Exception as e:
            click.echo(f"  ❌ Keep-last cleanup failed: {e}")
    
    # ── Pending tasks / outgoing queue cleanup ──
    if clean_all:
        try:
            conn = sqlite3.connect(str(DB_PATH))
            for table in ["pending_tasks", "outgoing_queue"]:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                if count:
                    if dry_run:
                        click.echo(f"  [DRY RUN] Would clear {count} items from {table}")
                    else:
                        conn.execute(f"DELETE FROM {table}")
                        click.echo(f"  🗑️  Cleared {count} items from {table}")
                        total_freed += count
            conn.commit()
            conn.close()
        except Exception as e:
            click.echo(f"  ❌ Queue cleanup failed: {e}")
    
    # ── Handshake PCAP cleanup ──
    if clean_handshakes > 0 or clean_all:
        handshake_dir = PROJECT_DIR / "handshakes"
        if handshake_dir.exists():
            cutoff_time = datetime.datetime.now() - datetime.timedelta(days=clean_handshakes) if clean_handshakes > 0 else datetime.datetime.now() + datetime.timedelta(days=1)
            
            for pcap in list(handshake_dir.glob("*.pcap")) + list(handshake_dir.glob("*.2500")):
                if clean_all or (clean_handshakes > 0 and datetime.datetime.fromtimestamp(pcap.stat().st_mtime) < cutoff_time):
                    if dry_run:
                        click.echo(f"  [DRY RUN] Would delete {pcap.name}")
                    else:
                        pcap.unlink()
                        click.echo(f"  🗑️  Deleted handshake: {pcap.name}")
                        total_freed += 1
    
    # ── Vacuum DB ──
    if not dry_run and total_freed > 0:
        try:
            conn = sqlite3.connect(str(DB_PATH))
            before = Path(DB_PATH).stat().st_size
            conn.execute("VACUUM")
            conn.close()
            after = Path(DB_PATH).stat().st_size
            saved_mb = (before - after) / (1024 * 1024)
            if saved_mb > 0.1:
                click.echo(f"  💾 Database vacuum: {saved_mb:.1f} MB freed")
        except Exception as e:
            click.echo(f"  ❌ Vacuum failed: {e}")
    
    if dry_run:
        click.echo("  [DRY RUN] No changes made — pass --dry-run again to confirm")
    else:
        click.echo(f"  ✅ Cleanup complete: {total_freed} records/files freed")
        click.echo("  💡 Run 'gotchi doctor' to verify freed space")

@click.command()
@click.argument('action', required=False, default='tail')
@click.option('-f', '--follow', is_flag=True, help='Follow mode: stream logs in real-time with colorized output')
@click.option('--lines', type=int, default=50, help='Number of lines to show (default: 50)')
def logs(action, follow, lines):
    """Stream or manage bot logs. Actions: tail, clear, extended."""
    import shutil
    if not shutil.which("journalctl"):
        click.secho("⚠️  journalctl is not available on this system (Linux-only systemd logger).", fg='bright_yellow', bold=True)
        click.echo("On macOS / local PC deployments, the bot outputs its logs directly to stdout/stderr.")
        click.echo("To view live logs, launch your bot in the foreground via:")
        click.secho("   gotchi run-bot", fg='bright_cyan', bold=True)
        return

    if action == 'clear':
        subprocess.run(["sudo", "journalctl", "--vacuum-time=1s"])
        return
    elif action == 'extended':
        subprocess.run(["journalctl", "-u", "gotchi"])
        return

    # tail or default: colorize output
    do_follow = follow or (action == 'tail' and lines > 0)
    cmd = ["journalctl", "-u", "gotchi", "-n", str(lines)]
    if do_follow:
        cmd.append("-f")

    def _colorize(line: str) -> str:
        """Apply ANSI color codes based on log line content."""
        if 'ERROR' in line:
            return f"\033[91m{line}\033[0m"
        if 'WARNING' in line:
            return f"\033[93m{line}\033[0m"
        if any(m in line for m in ('heartbeat', '💬', '🧠')):
            return f"\033[96m{line}\033[0m"
        if any(m in line for m in ('pwn', '📡', '📶')):
            return f"\033[95m{line}\033[0m"
        return f"\033[0m{line}\033[0m"

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for raw_line in proc.stdout:
            click.echo(_colorize(raw_line.rstrip('\n')))
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
    except Exception as e:
        click.echo(f"Failed to stream logs: {e}", err=True)

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
    from core.registry import get_registered_tools, load_all_extensions
    load_all_extensions(str(PROJECT_DIR / "src" / "extensions"))
    tools = get_registered_tools()
    format_header("Available Tools")
    for name in tools:
        click.echo(f"• {name}")

@click.group()
def ui():
    """UI and Display configuration."""

@ui.command(name="mode")
@click.argument('mode_setting', type=click.Choice(['dark', 'light'], case_sensitive=False))
def ui_mode(mode_setting):
    """Set the e-Paper display mode (dark or light)."""
    from core.cli.utils import success_print
    from core.commands import set_env_var
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
    """Launch the live web dashboard server."""
    click.echo(f"Starting live web dashboard on port {port}...")
    import socket

    from ui.web_dash import ThreadingHTTPServer, WebDashboardHandler
    
    # Try to get the actual network IP address
    hostname = socket.gethostname()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    try:
        server = ThreadingHTTPServer(("0.0.0.0", port), WebDashboardHandler)
        click.secho(f"✓ Dashboard running and bound to 0.0.0.0:{port}", fg='bright_green', bold=True)
        click.echo("Access it from other devices using:")
        if local_ip != "127.0.0.1":
            click.secho(f"  ➜ Network IP : http://{local_ip}:{port}", fg='bright_cyan')
        click.secho(f"  ➜ Hostname   : http://{hostname}.local:{port}", fg='bright_cyan')
        click.secho(f"  ➜ Localhost  : http://localhost:{port}", fg='bright_cyan')
        click.echo("")
        click.echo("Press Ctrl+C to stop the server.")
        server.serve_forever()
    except Exception as e:
        click.echo(f"Error starting web server: {e}", err=True)


@click.group()
def config():
    """Manage bot configuration."""


@config.command()
@click.option('--interactive', is_flag=True, default=True)
def init(interactive):
    """Interactive configuration wizard to set up API keys and hardware settings."""
    click.echo("=== 🦋 Gotchi Configuration Wizard ===")
    click.echo("Press Enter to skip any field. Existing values shown in brackets.\n")

    import os
    from pathlib import Path
    env_path = Path('/root/openclawgotchi/.env')

    # Read current .env
    env_vars = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()

    def prompt_field(name, desc, default=''):
        current = env_vars.get(name, default)
        prompt = f"  {desc} [{current}]: " if current else f"  {desc}: "
        val = input(prompt).strip()
        return val if val else current

    # Bot Identity
    click.echo("\n--- Bot Identity ---")
    bot_name = prompt_field('BOT_NAME', 'Bot name', 'Gotchi')
    owner = prompt_field('OWNER_NAME', 'Your name')

    # Platform
    click.echo("\n--- Chat Platform ---")
    platform = prompt_field('BOT_PLATFORM', 'Platform (discord/telegram)', 'discord')
    if platform == 'discord':
        prompt_field('DISCORD_BOT_TOKEN', 'Discord Bot Token')
        prompt_field('DISCORD_CHANNEL_ID', 'Discord Channel ID')
    elif platform == 'telegram':
        prompt_field('TELEGRAM_BOT_TOKEN', 'Telegram Bot Token')

    # LLM
    click.echo("\n--- LLM Provider (pick one) ---")
    click.echo("  Supported: deepseek, openrouter, google, openai, anthropic, groq")
    provider = prompt_field('DEFAULT_LITE_PRESET', 'LLM provider', 'deepseek')
    key_map = {
        'deepseek': 'DEEPSEEK_API_KEY',
        'openrouter': 'OPENROUTER_API_KEY',
        'google': 'GOOGLE_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
    }
    if provider in key_map:
        prompt_field(key_map[provider], f'{provider.title()} API Key')

    # Hardware
    click.echo("\n--- Hardware ---")
    mock = prompt_field('MOCK_HARDWARE', 'Mock hardware mode? (0=real Pi, 1=simulator)', '0')
    hunt = prompt_field('HUNT_ON_BOOT', 'Auto-start Wi-Fi hunting on boot? (true/false)', 'false')

    # Dashboard auth
    click.echo("\n--- Web Dashboard ---")
    dash_token = prompt_field('DASHBOARD_TOKEN', 'Dashboard auth token (optional)')

    # Write .env
    lines = []
    for key in ['BOT_NAME', 'OWNER_NAME', 'BOT_PLATFORM', 'DISCORD_BOT_TOKEN', 'DISCORD_CHANNEL_ID',
                'TELEGRAM_BOT_TOKEN', 'DEFAULT_LITE_PRESET', 'DEEPSEEK_API_KEY', 'OPENROUTER_API_KEY',
                'GOOGLE_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'MOCK_HARDWARE',
                'HUNT_ON_BOOT', 'DASHBOARD_TOKEN']:
        if key in env_vars or key in ['BOT_NAME', 'BOT_PLATFORM', 'MOCK_HARDWARE', 'HUNT_ON_BOOT']:
            val = env_vars.get(key, '')
            if val:
                lines.append(f'{key}={val}')
    lines.append('')
    env_path.write_text('\n'.join(lines))
    click.echo(f"\n✅ Configuration saved to {env_path}")
    click.echo("  Run 'gotchi doctor' to verify your setup.")
