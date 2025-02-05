"""Configuration management for the Nimba SMS CLI.

This module handles loading and saving configuration settings such as API credentials.
"""

from pathlib import Path
from typing import Optional
import json

from pydantic import BaseModel


class Credentials(BaseModel):
    """API credentials model."""

    service_id: Optional[str] = None
    secret_token: Optional[str] = None


class ConfigManager:
    """Manages CLI configuration and credentials."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize configuration manager.

        Args:
            config_dir: Optional custom config directory path.
        """
        self.config_dir = config_dir or Path.home() / ".config" / "nimbasms"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()

    def ensure_config_dir(self) -> None:
        """Create configuration directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_credentials(self) -> Credentials:
        """Load credentials from config file.

        Returns:
            Credentials object containing service_id and secret_token.
        """
        if not self.config_file.exists():
            return Credentials()

        try:
            with self.config_file.open() as f:
                data = json.load(f)
                return Credentials(**data)
        except (json.JSONDecodeError, OSError):
            return Credentials()

    def save_credentials(
        self, service_id: Optional[str] = None, secret_token: Optional[str] = None
    ) -> None:
        """Save credentials to config file.

        Only updates the specified credentials, keeping existing values for unspecified ones.

        Args:
            service_id: Optional service ID to save.
            secret_token: Optional secret token to save.
        """
        current = self.load_credentials()
        new_creds = Credentials(
            service_id=service_id or current.service_id,
            secret_token=secret_token or current.secret_token,
        )

        with self.config_file.open("w") as f:
            json.dump(new_creds.model_dump(), f, indent=2)


# Global instance for use throughout the application
config = ConfigManager()