"""Extension management commands."""

from pathlib import Path
from typing import Optional
from uuid import UUID

import typer
import json
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from httpx import HTTPStatusError

from ..config.settings import config as settings
from ..core.api import APIClient
from ..core.types import CreateExtension, AuthType

app = typer.Typer(help="Manage extensions")
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
def list_extensions(
    limit: int = typer.Option(10, help="Maximum number of extensions to show"),
    offset: int = typer.Option(0, help="Number of extensions to skip"),
    output: str = typer.Option("table", help="Output format (table/json)"),
) -> None:
    """List available extensions."""
    try:
        client = _get_client()
        extensions = client.list_extensions(limit=limit, offset=offset)

        if not extensions:
            console.print("\n[yellow]No extensions found.[/yellow]\n")
            return

        if output == "json":
            console.print(json.dumps([ext.model_dump(mode='json') for ext in extensions], indent=2))
            return

        for i, ext in enumerate(extensions, 1):
            if i > 1:
                console.print("─" * 80)  # Separator between extensions
            
            console.print(f"[cyan]Extension {i}:[/cyan]")
            console.print(f"[bold]ID:[/bold] {ext.extensionid}")
            console.print(f"[bold]Name:[/bold] {ext.name}")
            console.print(f"[bold]Description:[/bold] {ext.description}")
            console.print(f"[bold]Auth Type:[/bold] {ext.auth_type.value}")
            console.print(f"[bold]Status:[/bold] {'✓ Published' if ext.is_published else 'Draft'}")
            console.print(f"[bold]Approved:[/bold] {'✓ Yes' if ext.is_approved else 'No'}")
            
            if ext.documentation_url:
                console.print(f"[bold]Documentation:[/bold] {ext.documentation_url}")
            if ext.website_url:
                console.print(f"[bold]Website:[/bold] {ext.website_url}")
            
            console.print(f"[bold]Created:[/bold] {ext.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        console.print("\n")

    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Option(..., help="Extension name"),
    category: str = typer.Option(..., help="Extension category"),
    description: str = typer.Option(..., help="Extension description"),
    base_api_url: str = typer.Option(..., help="Base API URL"),
    auth_type: AuthType = typer.Option(
        AuthType.NONE, help="Authentication type (none/api_key/oauth2)"
    ),
    is_paid: bool = typer.Option(False, help="Is this a paid extension?"),
    docs_url: Optional[str] = typer.Option(None, help="Documentation URL"),
    website_url: Optional[str] = typer.Option(None, help="Website URL"),
) -> None:
    """Create a new extension."""
    try:
        client = _get_client()
        
        ext_data = CreateExtension(
            name=name,
            category=category,
            description=description,
            base_api_url=base_api_url,
            auth_type=auth_type,
            is_paid=is_paid,
            documentation_url=docs_url,
            website_url=website_url,
        )
        
        extension = client.create_extension(ext_data)
        
        console.print("\n[green]Extension created successfully![/green]")
        console.print(f"\nExtension ID: {extension.extensionid}")
        console.print(f"Status: {'Published' if extension.is_published else 'Draft'}")
        
    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def get(
    extension_id: UUID = typer.Argument(..., help="Extension ID"),
    output: str = typer.Option("table", help="Output format (table/json)", ),
) -> None:
    """Get extension details."""
    try:
        client = _get_client()
        extension = client.get_extension(extension_id)

        if output == "json":
            data = extension.model_dump(mode='json')
            console.print_json(json.dumps(data, indent=2, default=str))
            return

        console.print("\n[bold]Extension Details:[/bold]")
        console.print(f"\nID: {extension.extensionid}")
        console.print(f"Name: {extension.name}")
        console.print(f"Description: {extension.description}")
        console.print(f"Auth Type: {extension.auth_type.value}")
        console.print(f"Base API URL: {extension.base_api_url}")
        console.print(f"Status: {'✓ Published' if extension.is_published else 'Draft'}")
        console.print(f"Approved: {'✓ Yes' if extension.is_approved else 'No'}")
        if extension.documentation_url:
            console.print(f"Documentation: {extension.documentation_url}")
        if extension.website_url:
            console.print(f"Website: {extension.website_url}")
        console.print(f"Created: {extension.created_at}")
        console.print(f"Last Updated: {extension.updated_at}")
        console.print("")

    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def update(
    extension_id: UUID = typer.Argument(..., help="Extension ID"),
    name: Optional[str] = typer.Option(None, help="New name"),
    description: Optional[str] = typer.Option(None, help="New description"),
    base_api_url: Optional[str] = typer.Option(None, help="New base API URL"),
    docs_url: Optional[str] = typer.Option(None, help="New documentation URL"),
    website_url: Optional[str] = typer.Option(None, help="New website URL"),
) -> None:
    """Update extension details."""
    try:
        client = _get_client()
        
        update_data = {}
        if name:
            update_data["name"] = name
        if description:
            update_data["description"] = description
        if base_api_url:
            update_data["base_api_url"] = base_api_url
        if docs_url:
            update_data["documentation_url"] = docs_url
        if website_url:
            update_data["website_url"] = website_url

        if not update_data:
            console.print("[yellow]No updates provided.[/yellow]")
            return

        extension = client.update_extension(extension_id, update_data)
        console.print("\n[green]Extension updated successfully![/green]")
        
    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def upload_logo(
    extension_id: UUID = typer.Argument(..., help="Extension ID"),
    logo_path: Path = typer.Argument(..., help="Path to logo file"),
) -> None:
    """Upload extension logo."""
    try:
        client = _get_client()
        extension = client.upload_logo(extension_id, logo_path)
        console.print("\n[green]Logo uploaded successfully![/green]")
        
    except FileNotFoundError:
        console.print(f"[red]Error: Logo file not found: {logo_path}[/red]")
        raise typer.Exit(1)
    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def publish(
    extension_id: UUID = typer.Argument(..., help="Extension ID"),
) -> None:
    """Publish an extension."""
    try:
        client = _get_client()
        status = client.publish_action(extension_id)
        console.print("\n[green]Extension published successfully![/green]")
        
    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)