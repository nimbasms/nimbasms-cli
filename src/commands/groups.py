"""Group management commands."""

from typing import Optional
from uuid import UUID
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from httpx import HTTPStatusError

from ..config.settings import config as settings
from ..core.api import APIClient
from ..core.utils import format_timestamp

app = typer.Typer(help="Manage contact groups")
console = Console()


def _get_client() -> APIClient:
    """Get configured API client.

    Returns:
        Configured API client.

    Raises:
        typer.Exit: If credentials are not configured.
    """
    creds = settings.load_credentials()
    if not creds.service_id or not creds.secret_token:
        console.print("[red]Error: API credentials not configured.[/red]")
        console.print("\nPlease configure your credentials using:")
        console.print("  nimbasms config set service_id YOUR_SERVICE_ID")
        console.print("  nimbasms config set secret_token YOUR_SECRET_TOKEN")
        raise typer.Exit(1)

    return APIClient(creds.service_id, creds.secret_token)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Callback to handle no command."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@app.command("list")
def list_groups(
    limit: int = typer.Option(10, help="Maximum number of groups to show"),
    offset: int = typer.Option(0, help="Number of groups to skip"),
    output: str = typer.Option("table", help="Output format (table/json)"),
) -> None:
    """List contact groups."""
    try:
        client = _get_client()
        groups = client.list_groups(limit=limit, offset=offset)

        if not groups:
            console.print("\n[yellow]No groups found.[/yellow]\n")
            return

        if output == "json":
            import json
            console.print(json.dumps([group.model_dump(mode='json') for group in groups], indent=2))
            return

        # Create table
        table = Table(show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Total Contacts", style="blue", justify="right")
        table.add_column("Created", style="yellow")

        for group in groups:
            # Tronquer l'UUID à une longueur raisonnable
            short_id = str(group.groupe_id)[:8] + "..."
            table.add_row(
                short_id,
                group.name,
                str(group.total_contact),
                format_timestamp(group.added_at)
            )

        console.print("\n")
        console.print(table)
        console.print("\n")

    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(code=1)