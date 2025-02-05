"""Message management commands."""

from typing import Optional, List
from uuid import UUID

import typer
from rich.console import Console
from httpx import HTTPStatusError

from ..config.settings import config as settings
from ..core.api import APIClient
from ..core.types import CreateMessage
from ..core.utils import format_timestamp

app = typer.Typer(help="Manage SMS messages")
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
def list_messages(
    limit: int = typer.Option(10, help="Maximum number of messages to show"),
    offset: int = typer.Option(0, help="Number of messages to skip"),
    status: Optional[str] = typer.Option(None, help="Filter by status (pending/sent/failure)"),
    output: str = typer.Option("table", help="Output format (table/json)"),
) -> None:
    """List SMS messages with optional filtering."""
    try:
        client = _get_client()
        messages = client.list_messages(limit=limit, offset=offset, status=status)

        if not messages:
            console.print("\n[yellow]No messages found.[/yellow]\n")
            return

        if output == "json":
            import json
            console.print(json.dumps([msg.model_dump(mode='json') for msg in messages], indent=2))
            return

        for i, msg in enumerate(messages, 1):
            if i > 1:
                console.print("─" * 80)
            
            console.print(f"\n")
            console.print(f"[bold]ID:[/bold] {msg.messageid}")
            console.print(f"[bold]From:[/bold] {msg.sender_name}")
            console.print(f"[bold]Status:[/bold] {msg.status.value}")
            console.print(f"[bold]Message:[/bold] {msg.message}")
            console.print(f"[bold]Sent:[/bold] {format_timestamp(msg.sent_at)}")
            
            if msg.numbers:
                console.print("\n[bold]Delivery Status:[/bold]")
                for number in msg.numbers:
                    status_color = {
                        "received": "green",
                        "sent": "yellow",
                        "failure": "red",
                    }.get(number.status.value, "white")
                    console.print(f"  • {number.contact}: [{status_color}]{number.status.value}[/{status_color}]")

        console.print("\n")

    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def send(
    to: List[str] = typer.Option(..., "--to", help="Recipient phone number(s)"),
    sender: str = typer.Option(..., help="Sender name (max 11 chars)"),
    message: str = typer.Option(..., help="Message content"),
) -> None:
    """Send a new SMS message."""
    try:
        client = _get_client()
        
        msg_data = CreateMessage(
            sender_name=sender,
            to=to,
            message=message
        )
        
        response = client.send_message(msg_data)
        
        console.print("\n[green]Message sent successfully![/green]")
        console.print(f"\nMessage ID: {response.messageid}")
        console.print(f"Status URL: {response.url}")
        console.print("")
        
    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def get(
    message_id: UUID = typer.Argument(..., help="Message ID"),
    output: str = typer.Option("table", help="Output format (table/json)"),
) -> None:
    """Get message details and delivery status."""
    try:
        client = _get_client()
        message = client.get_message(message_id)
        
        if output == "json":
            import json
            console.print(json.dumps(message.model_dump(mode='json'), indent=2))
            return

        console.print("\n[bold cyan]Message Details:[/bold cyan]")
        console.print(f"\n[bold]ID:[/bold] {message.messageid}")
        console.print(f"[bold]From:[/bold] {message.sender_name}")
        console.print(f"[bold]Status:[/bold] {message.status.value}")
        console.print(f"[bold]Message:[/bold] {message.message}")
        console.print(f"[bold]Sent:[/bold] {format_timestamp(message.sent_at)}")
        
        if message.numbers:
            console.print("\n[bold]Delivery Status:[/bold]")
            for number in message.numbers:
                status_color = {
                    "received": "green",
                    "sent": "yellow",
                    "failure": "red",
                }.get(number.status.value, "white")
                console.print(f"  • {number.contact}: [{status_color}]{number.status.value}[/{status_color}]")
        
        console.print("\n")
        
    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)