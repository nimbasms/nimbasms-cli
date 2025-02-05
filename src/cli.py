"""Main CLI entry point for Nimba SMS."""

from typing import Optional

import typer
from rich.console import Console

from src.commands import accounts
from src.commands import extensions
from src.commands import messages
from src.commands import contacts
from src.commands import groups
from src.commands import sendernames
from src.commands import verifications
from src.config.settings import config as settings

app = typer.Typer(
    help="Official CLI for Nimba SMS API",
    add_completion=False,
)

# Add sub-commands
app.add_typer(accounts.app, name="account", help="Manage account settings and information")
app.add_typer(extensions.app, name="extensions", help="Manage extensions")
app.add_typer(messages.app, name="messages", help="Manage Message")
app.add_typer(contacts.app, name="contacts", help="Manage Contact")
app.add_typer(groups.app, name="groups", help="Manage Groups")
app.add_typer(sendernames.app, name="sendernames", help="Manage SenderName")
app.add_typer(verifications.app, name="verifications", help="Manage Verification")

console = Console()


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context) -> None:
    """Show help if no command is provided."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@app.command()
def config(
    command: str = typer.Argument(..., help="Command to execute"),
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Configure CLI settings.

    Usage:
        nimbasms config set <key> <value>

    Available keys:
        service_id     - Your service identifier
        secret_token  - Your secret token

    Examples:
        nimbasms config set service_id YOUR_ID
        nimbasms config set secret_token YOUR_TOKEN
    """
    if command != "set":
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("\nUsage: nimbasms config set <key> <value>")
        console.print("\nAvailable keys:")
        console.print("  service_id     - Your service identifier")
        console.print("  secret_token   - Your secret token")
        raise typer.Exit(1)

    try:
        match key:
            case "service_id":
                settings.save_credentials(service_id=value, secret_token=None)
                console.print("[green]Service ID configured successfully![/green]")
            case "secret_token":
                settings.save_credentials(service_id=None, secret_token=value)
                console.print("[green]Secret token configured successfully![/green]")
            case _:
                console.print(f"[red]Unknown configuration key: {key}[/red]")
                raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()