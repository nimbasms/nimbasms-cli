"""Account management commands.

This module provides CLI commands for managing account-related actions
such as checking balance and webhook configuration.
"""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from httpx import HTTPStatusError

from ..config.settings import config
from ..core.api import APIClient

app = typer.Typer(help="Manage account settings and information")
console = Console()


def _check_credentials() -> tuple[str, str]:
    """Check if credentials are configured.

    Returns:
        Tuple of service_id and secret_token.

    Raises:
        typer.Exit: If credentials are not properly configured.
    """
    creds = config.load_credentials()
    if not creds.service_id or not creds.secret_token:
        console.print("[red]Error: API credentials not configured.[/red]")
        console.print(
            "\nPlease configure your credentials using:",
            style="yellow",
        )
        console.print("  nimbasms config set service_id YOUR_SERVICE_ID")
        console.print("  nimbasms config set secret_token YOUR_SECRET_TOKEN")
        raise typer.Exit(1)
    
    return creds.service_id, creds.secret_token


@app.command()
def balance() -> None:
    """Display account balance and information."""
    service_id, secret_token = _check_credentials()
    
    try:
        client = APIClient(service_id, secret_token)
        account = client.get_account()
        
        # Create rich table for display
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("SID")
        table.add_column("SMS Balance", style="green")
        table.add_column("Webhook URL", style="blue")
        
        table.add_row(
            account.sid,
            str(account.balance),
            account.webhook_url or "[yellow]Not configured[/yellow]"
        )
        
        console.print("")  # Empty line for better readability
        console.print(table)
        console.print("")  # Empty line for better readability
        
    except HTTPStatusError as e:
        match e.response.status_code:
            case 401:
                console.print("[red]Error: Invalid credentials[/red]")
            case 429:
                console.print("[red]Error: Rate limit exceeded[/red]")
            case _:
                console.print(
                    f"[red]Error: {e.response.json().get('detail', str(e))}[/red]"
                )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def webhook(url: Optional[str] = None) -> None:
    """Configure or display webhook URL.
    
    Args:
        url: New webhook URL to set. If not provided, displays current webhook.
    """
    # TODO: Implement webhook configuration once API supports it
    console.print("[yellow]Webhook configuration not yet implemented[/yellow]")