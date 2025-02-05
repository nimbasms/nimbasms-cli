"""Tests for account management commands."""

from typing import Generator
from unittest.mock import patch

import pytest
from typer.testing import CliRunner
from httpx import HTTPStatusError, Response

from src.commands.accounts import app
from src.core.api import Account


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI runner for testing.

    Returns:
        Configured CLI runner.
    """
    return CliRunner()


@pytest.fixture
def mock_credentials() -> Generator[None, None, None]:
    """Mock credentials configuration.

    Yields:
        None
    """
    with patch("src.commands.accounts.config.load_credentials") as mock:
        mock.return_value.service_id = "test_id"
        mock.return_value.secret_token = "test_token"
        yield mock


@pytest.fixture
def mock_account() -> Generator[None, None, None]:
    """Mock API account response.

    Yields:
        None
    """
    with patch("src.commands.accounts.APIClient.get_account") as mock:
        mock.return_value = Account(
            sid="test123",
            balance=1000,
            webhook_url="https://example.com/webhook"
        )
        yield mock


def test_balance_success(
    runner: CliRunner,
    mock_credentials,
    mock_account
) -> None:
    """Test successful balance command execution.

    Args:
        runner: CLI runner fixture.
        mock_credentials: Mocked credentials fixture.
        mock_account: Mocked account response fixture.
    """
    result = runner.invoke(app, ["balance"])
    assert result.exit_code == 0
    assert "test123" in result.stdout
    assert "1000" in result.stdout
    assert "https://example.com/webhook" in result.stdout


def test_balance_no_credentials(
    runner: CliRunner,
    mock_account
) -> None:
    """Test balance command with missing credentials.

    Args:
        runner: CLI runner fixture.
        mock_account: Mocked account response fixture.
    """
    with patch("src.commands.accounts.config.load_credentials") as mock:
        mock.return_value.service_id = None
        mock.return_value.secret_token = None
        
        result = runner.invoke(app, ["balance"])
        assert result.exit_code == 1
        assert "Error: API credentials not configured" in result.stdout


def test_balance_unauthorized(
    runner: CliRunner,
    mock_credentials
) -> None:
    """Test balance command with invalid credentials.

    Args:
        runner: CLI runner fixture.
        mock_credentials: Mocked credentials fixture.
    """
    with patch("src.commands.accounts.APIClient.get_account") as mock:
        mock.side_effect = HTTPStatusError(
            "Unauthorized",
            request=None,  # type: ignore
            response=Response(401)
        )
        
        result = runner.invoke(app, ["balance"])
        assert result.exit_code == 1
        assert "Error: Invalid credentials" in result.stdout


def test_balance_rate_limit(
    runner: CliRunner,
    mock_credentials
) -> None:
    """Test balance command when rate limited.

    Args:
        runner: CLI runner fixture.
        mock_credentials: Mocked credentials fixture.
    """
    with patch("src.commands.accounts.APIClient.get_account") as mock:
        mock.side_effect = HTTPStatusError(
            "Rate limited",
            request=None,  # type: ignore
            response=Response(429)
        )
        
        result = runner.invoke(app, ["balance"])
        assert result.exit_code == 1
        assert "Error: Rate limit exceeded" in result.stdout


def test_balance_unexpected_error(
    runner: CliRunner,
    mock_credentials
) -> None:
    """Test balance command with unexpected error.

    Args:
        runner: CLI runner fixture.
        mock_credentials: Mocked credentials fixture.
    """
    with patch("src.commands.accounts.APIClient.get_account") as mock:
        mock.side_effect = Exception("Unexpected error")
        
        result = runner.invoke(app, ["balance"])
        assert result.exit_code == 1
        assert "Unexpected error" in result.stdout


def test_balance_other_http_error(
    runner: CliRunner,
    mock_credentials
) -> None:
    """Test balance command with other HTTP error.

    Args:
        runner: CLI runner fixture.
        mock_credentials: Mocked credentials fixture.
    """
    with patch("src.commands.accounts.APIClient.get_account") as mock:
        mock.side_effect = HTTPStatusError(
            "Server error",
            request=None,  # type: ignore
            response=Response(500, json={"detail": "Internal server error"})
        )
        
        result = runner.invoke(app, ["balance"])
        assert result.exit_code == 1
        assert "Error: Internal server error" in result.stdout


def test_webhook_command(runner: CliRunner) -> None:
    """Test webhook command.

    Args:
        runner: CLI runner fixture.
    """
    result = runner.invoke(app, ["webhook"])
    assert result.exit_code == 0
    assert "Webhook configuration not yet implemented" in result.stdout