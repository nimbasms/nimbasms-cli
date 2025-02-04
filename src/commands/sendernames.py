"""Sender names management commands."""

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

app = typer.Typer(help="Manage sender names")
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
def list_sendernames(
    limit: int = typer.Option(10, help="Maximum number of sender names to show"),
    offset: int = typer.Option(0, help="Number of sender names to skip"),
    output: str = typer.Option("table", help="Output format (table/json)"),
) -> None:
    """List sender names."""
    try:
        client = _get_client()
        sendernames = client.list_sender_names(limit=limit, offset=offset)

        if not sendernames:
            console.print("\n[yellow]No sender names found.[/yellow]\n")
            return

        if output == "json":
            import json
            console.print(json.dumps([sn.model_dump(mode='json') for sn in sendernames], indent=2))
            return

        # Create table
        table = Table(show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Added", style="blue")

        for sn in sendernames:
            # Colorize status
            status_color = {
                "accepted": "green",
                "pending": "yellow",
                "refused": "red"
            }.get(sn.status, "white")

            table.add_row(
                str(sn.sendername_id)[:8] + "...",
                sn.name,
                f"[{status_color}]{sn.status}[/{status_color}]",
                format_timestamp(sn.added_at)
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