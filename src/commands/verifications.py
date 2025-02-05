"""Verification code management commands."""

from typing import Optional
from uuid import UUID

import typer
from rich.console import Console
from rich.table import Table
from httpx import HTTPStatusError

from ..config.settings import config as settings
from ..core.api import APIClient
from ..core.types import RequestVerification, CheckVerification

app = typer.Typer(help="Manage verification codes")
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


@app.command()
def create(
    to: str = typer.Option(..., help="Phone number to send verification to"),
    message: Optional[str] = typer.Option(
        None,
        help="Custom message template. Use <1234> as placeholder for the code."
    ),
    sender: Optional[str] = typer.Option(None, help="Sender name (max 11 chars)"),
    expiry: Optional[int] = typer.Option(
        None,
        help="Code expiry time in minutes (5-30)",
        min=5,
        max=30
    ),
    attempts: Optional[int] = typer.Option(
        None,
        help="Maximum verification attempts (3-10)",
        min=3,
        max=10
    ),
    code_length: Optional[int] = typer.Option(
        None,
        help="Verification code length (4-8)",
        min=4,
        max=8
    ),
    output: str = typer.Option("table", help="Output format (table/json)"),
) -> None:
    """Create a new verification request."""
    try:
        client = _get_client()
        
        verification_data = RequestVerification(
            to=to,
            message=message,
            sender_name=sender,
            expiry_time=expiry,
            attempts=attempts,
            code_length=code_length,
        )
        
        verification = client.create_verification(verification_data)
        
        if output == "json":
            import json
            def json_serializer(obj):
                """Custom JSON serializer for UUID and other objects."""
                if isinstance(obj, UUID):
                    return str(obj)
                return str(obj)  # Pour tout autre type non sérialisable
                
            console.print(json.dumps(
                verification.model_dump(mode='json', exclude_none=True),
                default=json_serializer,
                indent=2
            ))
            return

        console.print("\n[green]Verification request created successfully![/green]")
        console.print(f"\n[bold]Verification ID:[/bold] {verification.verificationid}")
        if verification.url:
            console.print(f"[bold]Status URL:[/bold] {verification.url}")
        console.print("\n[yellow]Note: Save the verification ID to verify the code later.[/yellow]")
        console.print("")
        
    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        raise e
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(code=1)


@app.command()
def verify(
    verification_id: UUID = typer.Argument(..., help="Verification request ID"),
    code: int = typer.Option(..., help="Verification code to check"),
    output: str = typer.Option("table", help="Output format (table/json)"),
) -> None:
    """Verify a code."""
    try:
        client = _get_client()
        
        verification_check = CheckVerification(code=code)
        result = client.check_verification(verification_id, verification_check)
        
        if output == "json":
            import json
            console.print(json.dumps(result.model_dump(mode='json'), indent=2))
            return

        status_color = {
            "approved": "green",
            "pending": "yellow",
            "failure": "red",
            "expired": "red",
            "too_many_attempts": "red"
        }.get(result.status.value, "white")

        console.print(f"\nStatus: [{status_color}]{result.status.value}[/{status_color}]")
        
        if result.status.value == "approved":
            console.print("[green]✓ Code verified successfully![/green]")
        elif result.status.value == "expired":
            console.print("[red]✗ Code has expired.[/red]")
        elif result.status.value == "too_many_attempts":
            console.print("[red]✗ Too many failed attempts.[/red]")
        elif result.status.value == "failure":
            console.print("[red]✗ Invalid code.[/red]")
        
        console.print("")
        
    except HTTPStatusError as e:
        console.print(f"[red]Error: {e.response.json().get('detail', str(e))}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(code=1)