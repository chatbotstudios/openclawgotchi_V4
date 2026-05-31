import json
import click

def output_result(data, as_json=False):
    """Universal output handler for human or machine consumption."""
    if as_json:
        # Filter out complex objects for JSON
        if hasattr(data, '__dict__'):
            data = data.__dict__
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if isinstance(data, str):
            click.echo(data)
        elif isinstance(data, dict):
            for k, v in data.items():
                key = k.replace("_", " ").title()
                click.secho(f"{key:15}: ", nl=False, fg='bright_blue', bold=True)
                click.echo(v)

def format_header(title):
    click.echo("")
    click.secho("╔" + "═" * (len(title) + 4) + "╗", fg='bright_blue', bold=True)
    click.secho(f"║  {title.upper()}  ║", fg='bright_blue', bold=True)
    click.secho("╚" + "═" * (len(title) + 4) + "╝", fg='bright_blue', bold=True)

def tactical_print(label, value, color='bright_blue'):
    """Prints a tactical key-value pair."""
    click.secho(f"[{label:^10}] ", nl=False, fg=color, bold=True)
    click.echo(value)

def success_print(msg):
    click.secho("  ✅ ", nl=False, fg='green', bold=True)
    click.echo(msg)

def error_print(msg):
    click.secho("  ❌ ", nl=False, fg='red', bold=True)
    click.echo(msg)
