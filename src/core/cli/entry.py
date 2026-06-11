import os
import sys
import click
from pathlib import Path

# Fix path to find src/
PROJECT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_DIR / "src"))

# Load environment
from dotenv import load_dotenv
load_dotenv(PROJECT_DIR / ".env")

# Ensure PYTHONPATH is set for sub-processes
os.environ["PYTHONPATH"] = str(PROJECT_DIR / "src")

from core.cli.commands.core import status, doctor, logs, restart, dash, clear, list_tools, ui, mode, help_cmd, run_bot, setup, serve
from core.cli.commands.pwn import pwn
from core.cli.commands.network import network
from core.cli.commands.tasks import tasks
from core.cli.commands.missions import missions
from game_engine.cli import aipet

class CategorizedGroup(click.Group):
    def format_commands(self, ctx, formatter):
        # Define categories mapping
        CATEGORIES = {
            "📡 Pwn & Wireless Auditing": [
                "pwn_status", "pwn_crack", "pwn_check_cracks", "pwn_show_qr", "pwn_hide_qr",
                "pwn_pause", "pwn_lock_target", "pwn_whitelist", "pwn_system_control",
                "pwn_ble_scan", "pwn_ble_track", "pwn_ble_purge", "pwn"
            ],
            "🌐 Networking & Tethering": [
                "net_scan", "net_connect", "net_status", "tether_scan", "tether_pair",
                "tether_up", "tether_status", "manage_wifi_interface", "manage_ble_adapter",
                "manage_net", "network", "net_list_saved", "net_forget", "net_show_password"
            ],
            "⏰ Scheduling & Automation": [
                "create_reminder", "manage_cron", "manage_reminders", "list_my_cron_jobs",
                "create_recurring_task", "delete_cron_job", "add_scheduled_task",
                "list_scheduled_tasks", "remove_scheduled_task", "tasks"
            ],
            "🧠 Knowledge & Memory": [
                "recall_memory", "remember_fact", "recall_facts", "recall_messages",
                "write_daily_log", "flush_context", "read_file", "write_file",
                "list_directory", "list_tree", "restore_from_backup", "clear"
            ],
            "🖼️ Hardware Interface": [
                "show_face", "add_custom_face", "ui"
            ],
            "⚙️ System Diagnostics & Administration": [
                "status", "doctor", "logs", "restart", "dash", "mode", "help", "run-bot",
                "list", "execute_bash", "run_cli", "git_command", "manage_service",
                "check_syntax", "restart_self", "safe_restart", "health_check", "log_error",
                "log_change", "read_architecture", "create_custom_tool", "read_vercel_skill",
                "check_mail", "get_status_report", "get_system_time", "set_llm_mode", "aipet", "backup"
            ]
        }
        
        # Build category lists of (command_name, command_help)
        rows_by_cat = {cat: [] for cat in CATEGORIES}
        uncategorized = []
        
        for name in self.list_commands(ctx):
            cmd = self.get_command(ctx, name)
            if cmd is None:
                continue
            
            help_str = cmd.get_short_help_str()
            
            # Find category
            found = False
            for cat, command_names in CATEGORIES.items():
                if name in command_names:
                    rows_by_cat[cat].append((name, help_str))
                    found = True
                    break
            
            if not found:
                uncategorized.append((name, help_str))
                
        # Format each category
        for cat, rows in rows_by_cat.items():
            if rows:
                with formatter.section(cat):
                    formatter.write_dl(rows)
                    
        if uncategorized:
            with formatter.section("Other Commands"):
                formatter.write_dl(uncategorized)

@click.group(cls=CategorizedGroup)
def cli():
    """🦋 OPENCLAWGOTCHI V3 — Tactical CLI Interface"""
    pass

from core.cli.commands.core import status, doctor, logs, restart, dash, clear, list_tools, ui, mode, help_cmd, run_bot, setup, serve, backup

# Register core commands
cli.add_command(status)
cli.add_command(backup)
cli.add_command(doctor)
cli.add_command(logs)
cli.add_command(restart)
cli.add_command(dash)
cli.add_command(clear)
cli.add_command(list_tools)
cli.add_command(ui)
cli.add_command(mode)
cli.add_command(help_cmd)
cli.add_command(run_bot)
cli.add_command(setup)
cli.add_command(serve)

# Register groups
cli.add_command(pwn)
cli.add_command(network)
cli.add_command(tasks)
cli.add_command(missions)
cli.add_command(aipet)

# --- Dynamic Tool CLI Registration ---
try:
    from core.registry import load_all_extensions, get_registered_tools
    
    # Load all extensions dynamically
    load_all_extensions(str(PROJECT_DIR / "src" / "extensions"))
    tools = get_registered_tools()
    
    # Custom Command for dynamic invocation
    class ToolCommand(click.Command):
        def __init__(self, name, func):
            import inspect
            doc = inspect.getdoc(func) or ""
            desc = doc.split("\n")[0] if doc else f"Run the {name} tool."
            super().__init__(name, help=desc)
            self.func = func
            
        def invoke(self, ctx):
            # Parse arguments in format k=v or positional
            kwargs = {}
            args = []
            for arg in ctx.args:
                if "=" in arg:
                    k, _, v = arg.partition("=")
                    # Stripping quotes if present
                    val = v.strip()
                    if val.startswith(('"', "'")) and val.endswith(('"', "'")):
                        val = val[1:-1]
                    kwargs[k.strip()] = val
                else:
                    args.append(arg)
            
            try:
                res = self.func(*args, **kwargs)
                click.echo(res)
            except Exception as e:
                click.echo(f"Error executing tool {self.name}: {e}", err=True)
                
    # Create a dynamic command for each registered tool
    for tool_name, func in tools.items():
        # Check if click command already exists with this name (avoid overriding static commands)
        if tool_name not in cli.commands:
            cmd = ToolCommand(tool_name, func)
            # Enable extra arguments parsing without throwing click options errors
            cmd.context_settings = dict(ignore_unknown_options=True, allow_extra_args=True)
            cli.add_command(cmd)
except Exception as e:
    print(f"Warning: Failed to dynamically register tools as CLI commands: {e}", file=sys.stderr)

def print_banner():
    pink = "\033[38;5;205m"
    blue = "\033[38;5;39m"
    bold = "\033[1m"
    reset = "\033[0m"
    
    banner = f"""
{pink}{bold}  ▄██████▄   ▄██████▄  ████████▄     ▄████████    ▄█    █▄   ▄█  
{pink}{bold} ▄█▀▀  ▀██▄ ▄█▀▀  ▀██▄ ███   ▀███   ▄███▀▀▀▀███   ▄███    ███ ▄███  
{pink}{bold} ███    ███ ███    ███ ███    ███   ███    ▀███   ███▌    ███  ███  
{blue}{bold} ███    ███ ███    ███ ███    ███  ▄███▄▄▄▄██▀    ███▌    ███  ███  
{blue}{bold} ███    ███ ███    ███ ███    ███ ▀▀███▀▀▀▀▀    ▀███████████  ███  
{blue}{bold} ███    ███ ███    ███ ███    ███ ▀███████████    ███▌    ███  ███  
{pink}{bold} ▀██▄  ▄██▀ ▀██▄  ▄██▀ ███   ▄███   ███    ███    ███     ███  ███  
{pink}{bold}  ▀██████▀   ▀██████▀  ████████▀    ███    ███     ██      ▀   ███  
{pink}{bold}                                    ███    ███                  {reset}"""
    print(banner)
    print(f"  {blue}OpenClawGotchi V3.0{reset} — {pink}Tactical Companion Core{reset}\n")

if __name__ == "__main__":
    # Check if setup sentinel exists. If not, and running without arguments, auto-launch setup wizard.
    sentinel_path = PROJECT_DIR / "workspace" / ".setup_completed"
    if not sentinel_path.exists() and len(sys.argv) <= 1:
        import subprocess
        wizard_path = PROJECT_DIR / "src" / "cli" / "wizard.mjs"
        try:
            subprocess.run(["node", str(wizard_path)])
            sys.exit(0)
        except Exception:
            pass
    if len(sys.argv) <= 1 or "--help" in sys.argv:
        print_banner()
    cli()
