import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from src.game_engine.state import load_state
from src.game_engine.vitals import add_xp, xp_to_reach_level
from src.game_engine.missions import get_missions, trigger_dream
import sqlite3
from config import DB_PATH
from core.cli.utils import format_header

console = Console()

@click.group()
def aipet():
    """👾 AIPET Game Engine — Check vitals, level up, and manage missions."""
    pass

@aipet.command()
def status():
    """Display the AIPET's current vitals, level, and progress."""
    state = load_state()
    format_header("AIPET Core Status")
    
    current_level_start_xp = xp_to_reach_level(state.level) if state.level > 1 else 0
    next_level_xp = xp_to_reach_level(state.level + 1)
    
    xp_in_level = state.xp - current_level_start_xp
    xp_needed = next_level_xp - current_level_start_xp
    
    # Render Progress Bar
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=False
    ) as progress:
        task = progress.add_task(f"[bold magenta]LVL {state.level}[/bold magenta] XP", total=xp_needed, completed=xp_in_level)
    
    details = (
        f"[bold cyan]Total XP:[/bold cyan] {state.xp} / {next_level_xp}\n"
        f"[bold red]HP:[/bold red] {state.hp:.1f} / 100.0\n"
        f"[bold green]RP (Reputation):[/bold green] {state.rp:.1f}\n"
        f"[bold yellow]Mood:[/bold yellow] {state.current_mood}\n"
        f"[bold white]Missions Completed:[/bold white] {state.missions_completed}"
    )
    
    console.print(Panel(details, title="Vitals & Progression", border_style="cyan"))

@aipet.command(name="add-xp")
@click.argument('amount', type=int)
@click.option('--source', default="cli", help="Source of the XP")
def add_xp_cmd(amount, source):
    """Manually inject XP (useful for testing and mission rewards)."""
    state = load_state()
    old_level = state.level
    
    new_xp = add_xp(amount, source)
    
    # Reload state to check if leveled up
    new_state = load_state()
    
    click.echo(f"Added {amount} XP. Total XP is now {new_xp}.")
    if new_state.level > old_level:
        console.print(f"[bold green]🎉 LEVEL UP! You are now Level {new_state.level}![/bold green]")

@aipet.group()
def mission():
    """Manage AIPET missions and bounties."""
    pass

@mission.command(name="list")
def list_missions():
    """List all available and active missions."""
    missions = get_missions()
    if not missions:
        console.print("[yellow]No missions found in the database.[/yellow]")
        return
        
    table = Table(title="AIPET Missions")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Reward (XP)", justify="right", style="green")
    table.add_column("Status")

    for m in missions:
        status_color = "yellow" if m["status"] == "active" else "green" if m["status"] == "completed" else "white"
        table.add_row(
            str(m["id"]),
            m["name"],
            m["category"],
            f"+{m['xp_reward']}",
            f"[{status_color}]{m['status']}[/{status_color}]"
        )

    console.print(table)

@aipet.command()
def dream():
    """Manually invoke a dream session."""
    console.print("[bold magenta]Entering Dream State...[/bold magenta]")
    trigger_dream()
    console.print("[italic cyan]The AIPET drifts into sleep, processing the day's patterns and generating synthetic XP...[/italic cyan]")

@aipet.command()
@click.argument('name')
@click.argument('xp_reward', type=int)
@click.option('--category', default='Bounty', help='Mission category')
def inject(name, xp_reward, category):
    """Inject a custom bounty mission into the database."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute('''
            INSERT INTO aipet_missions (name, category, xp_reward, status, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, category, xp_reward, 'active', 'user'))
        conn.commit()
        conn.close()
        console.print(f"[bold green]Successfully injected bounty mission '{name}' for {xp_reward} XP![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to inject mission: {e}[/bold red]")

