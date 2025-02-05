"""Tests for message management commands."""

from datetime import datetime
from unittest.mock import patch, Mock
from uuid import UUID

import pytest
from typer.testing import CliRunner
from httpx import HTTPStatusError, Response

from src.commands.messages import app
from src.core.types import Message, MessageResponse, MessageStatus, DeliveryMessage


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
    with patch("src.commands.messages._get_client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_message() -> Message:
    """Create a sample message for testing.

    Returns:
        Sample message instance.
    """
    return Message(
        messageid=UUID("12345678-1234-5678-1234-567812345678"),
        sender_name="TEST",
        message="Test message",
        status=MessageStatus.SENT,
        sent_at=int(datetime.now().timestamp()),
        numbers=[
            DeliveryMessage(
                id=UUID("12345678-1234-5678-1234-567812345678"),
                contact="+224623000000",
                status=MessageStatus.RECEIVED
            )
        ]
    )


def test_list_messages_empty(runner: CliRunner, mock_client: Mock) -> None:
    """Test listing messages when none exist.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.list_messages.return_value = []
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No messages found" in result.stdout


def test_list_messages_success(
    runner: CliRunner,
    mock_client: Mock,
    sample_message: Message
) -> None:
    """Test successful message listing.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_message: Sample message fixture.
    """
    mock_client.list_messages.return_value = [sample_message]
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert str(sample_message.messageid) in result.stdout
    assert sample_message.sender_name in result.stdout
    assert sample_message.message in result.stdout


def test_list_messages_json(
    runner: CliRunner,
    mock_client: Mock,
    sample_message: Message
) -> None:
    """Test message listing in JSON format.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_message: Sample message fixture.
    """
    mock_client.list_messages.return_value = [sample_message]
    
    result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0
    
    import json
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["messageid"] == str(sample_message.messageid)
    assert data[0]["sender_name"] == sample_message.sender_name


def test_send_message_success(runner: CliRunner, mock_client: Mock) -> None:
    """Test successful message sending.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    message_id = UUID("12345678-1234-5678-1234-567812345678")
    mock_client.send_message.return_value = MessageResponse(
        messageid=message_id,
        url=f"https://api.nimbasms.com/v1/messages/{message_id}"
    )
    
    result = runner.invoke(app, [
        "send",
        "--to", "623000000",
        "--sender", "TEST",
        "--message", "Test message"
    ])
    
    assert result.exit_code == 0
    assert "Message sent successfully!" in result.stdout
    assert str(message_id) in result.stdout


def test_get_message_details(
    runner: CliRunner,
    mock_client: Mock,
    sample_message: Message
) -> None:
    """Test getting message details.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_message: Sample message fixture.
    """
    mock_client.get_message.return_value = sample_message
    
    result = runner.invoke(app, ["get", str(sample_message.messageid)])
    assert result.exit_code == 0
    assert str(sample_message.messageid) in result.stdout
    assert sample_message.sender_name in result.stdout
    assert sample_message.message in result.stdout


def test_get_message_json(
    runner: CliRunner,
    mock_client: Mock,
    sample_message: Message
) -> None:
    """Test getting message details in JSON format.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_message: Sample message fixture.
    """
    mock_client.get_message.return_value = sample_message
    
    result = runner.invoke(app, ["get", str(sample_message.messageid), "--output", "json"])
    assert result.exit_code == 0
    
    import json
    data = json.loads(result.stdout)
    assert data["messageid"] == str(sample_message.messageid)
    assert data["sender_name"] == sample_message.sender_name


def test_error_handling(runner: CliRunner, mock_client: Mock) -> None:
    """Test error handling in commands.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.list_messages.side_effect = HTTPStatusError(
        "Unauthorized",
        request=Mock(),
        response=Response(401, json={"detail": "Invalid credentials"})
    )
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 1
    assert "Error: Invalid credentials" in result.stdout