"""Tests for verification code management commands."""

from unittest.mock import patch, Mock
from uuid import UUID

import pytest
from typer.testing import CliRunner
from httpx import HTTPStatusError, Response

from src.commands.verifications import app
from src.core.types import RequestVerification, CheckVerification, VerificationStatus


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI runner for testing.

    Returns:
        Configured CLI runner instance.
    """
    return CliRunner()


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock API client.

    Returns:
        Mock API client.
    """
    with patch("src.commands.verifications._get_client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_verification() -> RequestVerification:
    """Create a sample verification request for testing.

    Returns:
        Sample verification request instance.
    """
    return RequestVerification(
        verificationid=UUID("12345678-1234-5678-1234-567812345678"),
        to="623000000",
        message="Your verification code: <1234>",
        sender_name="TEST",
        code_length=4,
        url="https://api.nimbasms.com/v1/verifications/12345678",
    )


def test_create_verification_success(
    runner: CliRunner,
    mock_client: Mock,
    sample_verification: RequestVerification
) -> None:
    """Test successful verification creation.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_verification: Sample verification fixture.
    """
    mock_client.create_verification.return_value = sample_verification
    
    result = runner.invoke(app, [
        "create",
        "--to", "623000000",
        "--message", "Your code: <1234>",
        "--sender", "TEST",
        "--code-length", "4"
    ])
    
    assert result.exit_code == 0
    assert "Verification request created successfully!" in result.stdout
    assert str(sample_verification.verificationid) in result.stdout


def test_create_verification_json(
    runner: CliRunner,
    mock_client: Mock,
    sample_verification: RequestVerification
) -> None:
    """Test verification creation with JSON output.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_verification: Sample verification fixture.
    """
    mock_client.create_verification.return_value = sample_verification
    
    result = runner.invoke(app, [
        "create",
        "--to", "623000000",
        "--output", "json"
    ])
    
    assert result.exit_code == 0
    
    import json
    data = json.loads(result.stdout)
    assert data["verificationid"] == str(sample_verification.verificationid)
    assert data["to"] == sample_verification.to


def test_verify_code_success(runner: CliRunner, mock_client: Mock) -> None:
    """Test successful code verification.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.check_verification.return_value = CheckVerification(
        code=1234,
        status=VerificationStatus.APPROVED
    )
    
    result = runner.invoke(app, [
        "verify",
        "12345678-1234-5678-1234-567812345678",
        "--code", "1234"
    ])
    
    assert result.exit_code == 0
    assert "Code verified successfully!" in result.stdout


def test_verify_code_expired(runner: CliRunner, mock_client: Mock) -> None:
    """Test expired code verification.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.check_verification.return_value = CheckVerification(
        code=1234,
        status=VerificationStatus.EXPIRED
    )
    
    result = runner.invoke(app, [
        "verify",
        "12345678-1234-5678-1234-567812345678",
        "--code", "1234"
    ])
    
    assert result.exit_code == 0
    assert "Code has expired" in result.stdout


def test_verify_code_too_many_attempts(runner: CliRunner, mock_client: Mock) -> None:
    """Test verification with too many attempts.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.check_verification.return_value = CheckVerification(
        code=1234,
        status=VerificationStatus.TOO_MANY_ATTEMPTS
    )
    
    result = runner.invoke(app, [
        "verify",
        "12345678-1234-5678-1234-567812345678",
        "--code", "1234"
    ])
    
    assert result.exit_code == 0
    assert "Too many failed attempts" in result.stdout


def test_verify_code_invalid(runner: CliRunner, mock_client: Mock) -> None:
    """Test invalid code verification.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.check_verification.return_value = CheckVerification(
        code=1234,
        status=VerificationStatus.FAILURE
    )
    
    result = runner.invoke(app, [
        "verify",
        "12345678-1234-5678-1234-567812345678",
        "--code", "1234"
    ])
    
    assert result.exit_code == 0
    assert "Invalid code" in result.stdout


def test_error_handling(runner: CliRunner, mock_client: Mock) -> None:
    """Test error handling in commands.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.create_verification.side_effect = HTTPStatusError(
        "Bad Request",
        request=Mock(),
        response=Response(400, json={"detail": "Invalid phone number"})
    )
    
    result = runner.invoke(app, [
        "create",
        "--to", "invalid"
    ])
    
    assert result.exit_code == 1
    assert "Error: Invalid phone number" in result.stdout