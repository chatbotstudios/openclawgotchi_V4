import click
from core.cli.utils import format_header
from core.commands import manage_cron

@click.group()
def tasks():
    """Manage cron tasks, reminders, and config."""
    pass

@tasks.group(name="cron")
def cron_group():
    """Manage recurring cron jobs."""
    pass

@cron_group.command(name="list")
def cron_list():
    """List scheduled bot tasks."""
    format_header("Scheduled Tasks")
    click.echo(manage_cron('list'))

@tasks.group()
def config():
    """Configuration management."""
    pass

@config.command(name="hunt-on-boot")
@click.argument('state', type=click.Choice(['on', 'off']))
def config_hunt(state):
    """Toggle auto-monitor on boot."""
    from core.commands import set_env_var
    val = "1" if state == "on" else "0"
    set_env_var("HUNT_ON_BOOT", val)
    click.echo(f"Hunt-On-Boot set to {state.upper()}")

@click.command()
@click.option('--interval', default=10)
def jobs(interval):
    """Live CPU/RAM/Service monitoring."""
    import psutil
    import time
    try:
        while True:
            click.clear()
            format_header("Tactical Monitor")
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            click.echo(f"CPU: {cpu}% | RAM: {mem.percent}%")
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
