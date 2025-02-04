"""Tests for the configuration management module."""

import json
from pathlib import Path

import pytest

from src.config.settings import ConfigManager, Credentials


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Create a temporary configuration directory.

    Args:
        tmp_path: Pytest fixture providing temporary directory.

    Returns:
        Path to temporary config directory.
    """
    return tmp_path / "config"


@pytest.fixture
def config_manager(temp_config_dir: Path) -> ConfigManager:
    """Create a ConfigManager instance with temporary directory.

    Args:
        temp_config_dir: Temporary config directory fixture.

    Returns:
        Configured ConfigManager instance.
    """
    return ConfigManager(temp_config_dir)


def test_config_dir_creation(config_manager: ConfigManager) -> None:
    """Test that configuration directory is created.

    Args:
        config_manager: ConfigManager fixture.
    """
    assert config_manager.config_dir.exists()
    assert config_manager.config_dir.is_dir()


def test_load_credentials_no_file(config_manager: ConfigManager) -> None:
    """Test loading credentials when no config file exists.

    Args:
        config_manager: ConfigManager fixture.
    """
    creds = config_manager.load_credentials()
    assert isinstance(creds, Credentials)
    assert creds.service_id is None
    assert creds.secret_token is None


def test_save_and_load_credentials(config_manager: ConfigManager) -> None:
    """Test saving and loading credentials.

    Args:
        config_manager: ConfigManager fixture.
    """
    config_manager.save_credentials(
        service_id="test_id",
        secret_token="test_token"
    )

    creds = config_manager.load_credentials()
    assert creds.service_id == "test_id"
    assert creds.secret_token == "test_token"


def test_partial_credentials_update(config_manager: ConfigManager) -> None:
    """Test updating only some credentials.

    Args:
        config_manager: ConfigManager fixture.
    """
    # Initial save
    config_manager.save_credentials(
        service_id="test_id",
        secret_token="test_token"
    )

    # Update only service_id
    config_manager.save_credentials(service_id="new_id")
    creds = config_manager.load_credentials()
    assert creds.service_id == "new_id"
    assert creds.secret_token == "test_token"

    # Update only secret_token
    config_manager.save_credentials(secret_token="new_token")
    creds = config_manager.load_credentials()
    assert creds.service_id == "new_id"
    assert creds.secret_token == "new_token"


def test_invalid_config_file(config_manager: ConfigManager) -> None:
    """Test handling of invalid config file.

    Args:
        config_manager: ConfigManager fixture.
    """
    # Write invalid JSON
    config_manager.config_file.write_text("invalid json")

    creds = config_manager.load_credentials()
    assert isinstance(creds, Credentials)
    assert creds.service_id is None
    assert creds.secret_token is None