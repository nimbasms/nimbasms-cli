"""Contact management commands."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from httpx import HTTPStatusError

from ..config.settings import config as settings
from ..core.api import APIClient
from ..core.types import CreateContact
from ..core.utils import format_timestamp

app = typer.Typer(help="Manage contacts")
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


@app.command("list")
def list_contacts(
    limit: int = typer.Option(10, help="Maximum number of contacts to show"),
    offset: int = typer.Option(0, help="Number of contacts to skip"),
    output: str = typer.Option("table", help="Output format (table/json)"),
) -> None:
    """List contacts with optional filtering."""
    try:
        client = _get_client()
        contacts = client.list_contacts(limit=limit, offset=offset)

        if not contacts:
            console.print("\n[yellow]No contacts found.[/yellow]\n")
            return

        if output == "json":
            import json
            console.print(json.dumps([contact.model_dump(mode='json') for contact in contacts], indent=2))
            return

        for i, contact in enumerate(contacts, 1):
            if i > 1:
                console.print("─" * 80)
            
            console.print(f"\n")
            console.print(f"[bold]ID:[/bold] {contact.contact_id}")
            console.print(f"[bold]Name:[/bold] {contact.name or 'N/A'}")
            console.print(f"[bold]Number:[/bold] {contact.numero}")
            if contact.groups:
                console.print(f"[bold]Groups:[/bold] {', '.join(contact.groups)}")
            console.print(f"[bold]Added:[/bold] {format_timestamp(contact.created_at)}")

        console.print("\n")

    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def add(
    numero: str = typer.Option(..., help="Phone number"),
    name: Optional[str] = typer.Option(None, help="Contact name"),
    groups: List[str] = typer.Option([], help="Groups to add the contact to"),
) -> None:
    """Add a new contact."""
    try:
        client = _get_client()
        
        contact_data = CreateContact(
            numero=numero,
            name=name,
            groups=groups
        )
        
        contact = client.create_contact(contact_data)
        
        console.print("\n[green]Contact added successfully![/green]")
        console.print(f"[bold]ID:[/bold] {contact.contact_id}")
        console.print(f"[bold]Name:[/bold] {contact.name or 'N/A'}")
        console.print(f"[bold]Number:[/bold] {contact.numero}")
        if contact.groups:
            console.print(f"[bold]Groups:[/bold] {', '.join(contact.groups)}")
        console.print("")
        
    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)