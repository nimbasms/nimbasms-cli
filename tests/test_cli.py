"""Tests for main CLI functionality."""

from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from src.cli import app


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI runner for testing.

    Returns:
        Configured CLI runner instance.
    """
    return CliRunner()


def test_main_no_args(runner: CliRunner) -> None:
    """Test CLI with no arguments shows help.

    Args:
        runner: CLI runner fixture.
    """
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Official CLI for Nimba SMS API" in result.stdout


def test_main_help(runner: CliRunner) -> None:
    """Test help command.

    Args:
        runner: CLI runner fixture.
    """
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Official CLI for Nimba SMS API" in result.stdout
    assert "Options" in result.stdout


def test_config_missing_args(runner: CliRunner) -> None:
    """Test config command with missing arguments.

    Args:
        runner: CLI runner fixture.
    """
    result = runner.invoke(app, ["config"])
    assert result.exit_code != 0
    assert "Missing argument" in result.stdout


def test_config_invalid_command(runner: CliRunner) -> None:
    """Test config with invalid sub-command.

    Args:
        runner: CLI runner fixture.
    """
    result = runner.invoke(app, ["config", "invalid", "service_id", "value"])
    assert result.exit_code == 1
    assert "Unknown command: invalid" in result.stdout
    assert "Usage: nimbasms config set <key> <value>" in result.stdout
    assert "service_id" in result.stdout
    assert "secret_token" in result.stdout


def test_config_set_service_id(runner: CliRunner) -> None:
    """Test setting service ID.

    Args:
        runner: CLI runner fixture.
    """
    with patch("src.config.settings.ConfigManager.save_credentials") as mock_save:
        result = runner.invoke(app, ["config", "set", "service_id", "test_id"])
        assert result.exit_code == 0
        assert "Service ID configured successfully!" in result.stdout
        mock_save.assert_called_once_with(service_id="test_id", secret_token=None)


def test_config_set_secret_token(runner: CliRunner) -> None:
    """Test setting secret token.

    Args:
        runner: CLI runner fixture.
    """
    with patch("src.config.settings.ConfigManager.save_credentials") as mock_save:
        result = runner.invoke(app, ["config", "set", "secret_token", "test_token"])
        assert result.exit_code == 0
        assert "Secret token configured successfully!" in result.stdout
        mock_save.assert_called_once_with(service_id=None, secret_token="test_token")


def test_config_set_invalid_key(runner: CliRunner) -> None:
    """Test setting invalid configuration key.

    Args:
        runner: CLI runner fixture.
    """
    result = runner.invoke(app, ["config", "set", "invalid_key", "value"])
    assert result.exit_code == 1
    assert "Unknown configuration key: invalid_key" in result.stdout


def test_config_set_error_handling(runner: CliRunner) -> None:
    """Test error handling when saving credentials.

    Args:
        runner: CLI runner fixture.
    """
    with patch("src.config.settings.ConfigManager.save_credentials") as mock_save:
        mock_save.side_effect = Exception("Test error")
        result = runner.invoke(app, ["config", "set", "service_id", "test_id"])
        assert result.exit_code == 1
        assert "Test error" in result.stdout


def test_config_help_message_display(runner: CliRunner) -> None:
    """Test config command help message display.

    Args:
        runner: CLI runner fixture.
    """
    result = runner.invoke(app, ["config", "invalid", "service_id", "value"])
    assert result.exit_code == 1
    assert "Usage: nimbasms config set <key> <value>" in result.stdout
    assert "service_id" in result.stdout
    assert "secret_token" in result.stdout
    assert "Your service identifier" in result.stdout