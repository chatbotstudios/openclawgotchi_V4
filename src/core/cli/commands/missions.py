import json
import click
from rich.console import Console
from rich.table import Table

from core.cli.utils import format_header, success_print
from core.missions.manager import get_missions, get_mission, update_mission_status

console = Console()

@click.group()
def missions():
    """🏆 Mission & Quest System — Manage your tactical objectives."""
    pass

@missions.command()
@click.option('--status', type=click.Choice(['available', 'active', 'completed', 'abandoned']), help="Filter by status")
@click.option('--category', help="Filter by category (e.g., tactical, daily)")
@click.option('--json', 'as_json', is_flag=True, help="Output in JSON format (machine-readable)")
def list(status, category, as_json):
    """List missions (active, available, completed)."""
    all_missions = get_missions(status)
    if category:
        all_missions = [m for m in all_missions if m.category.lower() == category.lower()]

    if as_json:
        missions_data = [
            {
                "id": m.id,
                "title": m.title,
                "description": getattr(m, 'description', ''),
                "category": m.category,
                "tier": m.tier,
                "actor": m.actor,
                "status": m.status,
                "progress": m.progress,
                "target": m.target,
                "reward_xp": m.reward_xp,
            }
            for m in all_missions
        ]
        click.echo(json.dumps(missions_data))
        return

    format_header(f"Gotchi Missions {('(' + status.upper() + ')') if status else ''}")
    if not all_missions:
        click.echo("No missions found.")
        return
        
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=15)
    table.add_column("Title")
    table.add_column("Category", justify="center")
    table.add_column("Tier", justify="center")
    table.add_column("Actor", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Progress", justify="right")
    table.add_column("XP", justify="right")
    
    for m in all_missions:
        status_color = "green" if m.status == 'completed' else "yellow" if m.status == 'active' else "white"
        prog_str = f"{m.progress}/{m.target}"
        table.add_row(
            m.id, 
            m.title, 
            m.category.title(),
            m.tier.upper(),
            m.actor.upper(),
            f"[{status_color}]{m.status}[/{status_color}]", 
            prog_str, 
            f"+{m.reward_xp}"
        )
        
    console.print(table)

@missions.command()
@click.argument('mission_id')
def accept(mission_id):
    """Accept a new mission."""
    m = get_mission(mission_id)
    if not m:
        click.secho(f"Mission '{mission_id}' not found.", fg="red")
        return
        
    if m.status != 'available':
        click.secho(f"Mission '{mission_id}' is already {m.status}.", fg="yellow")
        return
        
    update_mission_status(mission_id, 'active')
    success_print(f"Mission Accepted: {m.title}")
    click.echo(f"Objective: {m.description}")

@missions.command()
def active():
    """View active missions and progress."""
    format_header("Active Missions")
    active_m = get_missions("active")
    
    if not active_m:
        click.echo("You have no active missions. Run 'gotchi missions list' to find some!")
        return
        
    for m in active_m:
        click.secho(f"• {m.title} ({m.id})", fg="cyan", bold=True)
        click.echo(f"  {m.description}")
        click.echo(f"  Progress: {m.progress}/{m.target}  |  Reward: {m.reward_xp} XP\n")

@missions.command()
@click.option('--theme', default="random", help="Theme for the generated mission")
def generate(theme):
    """Generate a new mission via LLM."""
    format_header(f"Generating Mission: {theme}")
    click.echo(f"🤖 Contacting Gotchi Brain to generate a '{theme}' mission... (AI generation coming soon!)")
    click.echo("For now, use 'gotchi missions list' to see the 50 pre-loaded missions.")

@missions.command()
@click.argument('mission_id', required=False)
@click.pass_context
def progress(ctx, mission_id):
    """View progress for an active mission (or all)."""
    if not mission_id:
        ctx.invoke(active)
        return
        
    m = get_mission(mission_id)
    if not m:
        click.secho(f"Mission '{mission_id}' not found.", fg="red")
        return
        
    format_header(f"Mission Progress: {m.title}")
    click.echo(f"Status: {m.status}")
    
    # Progress bar using rich
    from rich.progress import Progress
    with Progress() as pb:
        task = pb.add_task("[cyan]Completion...", total=m.target, completed=m.progress)
        pb.update(task)

@missions.command()
@click.argument('mission_id')
def complete(mission_id):
    """Manually complete a mission and claim rewards."""
    m = get_mission(mission_id)
    if not m:
        click.secho(f"Mission '{mission_id}' not found.", fg="red")
        return
        
    if m.status == 'completed':
        click.secho("Mission is already completed!", fg="yellow")
        return
        
    from core.missions.rewards import dispense_mission_reward
    update_mission_status(mission_id, 'completed')
    
    # Update local object state so reward msg is accurate
    m.status = 'completed'
    m.progress = m.target
    
    dispense_mission_reward(m)
    success_print(f"Mission '{m.title}' forcibly completed! Rewards dispensed.")

@missions.command()
@click.pass_context
def history(ctx):
    """View completed mission history."""
    ctx.invoke(list, status="completed", category=None)

