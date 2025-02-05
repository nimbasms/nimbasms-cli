"""Tests for contact management commands."""

from unittest.mock import patch, Mock
from uuid import UUID
from datetime import datetime

import pytest
from typer.testing import CliRunner
from httpx import HTTPStatusError, Response

from src.commands.contacts import app
from src.core.types import Contact


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
    with patch("src.commands.contacts._get_client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_contact() -> Contact:
    """Create a sample contact for testing.

    Returns:
        Sample contact instance.
    """
    return Contact(
        contact_id=UUID("12345678-1234-5678-1234-567812345678"),
        name="John Doe",
        numero="623000000",
        created_at=int(datetime.now().timestamp()),
        groups=["VIP", "Customers"]
    )


def test_list_contacts_empty(runner: CliRunner, mock_client: Mock) -> None:
    """Test listing contacts when none exist.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.list_contacts.return_value = []
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No contacts found" in result.stdout


def test_list_contacts_success(
    runner: CliRunner,
    mock_client: Mock,
    sample_contact: Contact
) -> None:
    """Test successful contact listing.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_contact: Sample contact fixture.
    """
    mock_client.list_contacts.return_value = [sample_contact]
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert str(sample_contact.contact_id) in result.stdout
    assert sample_contact.name in result.stdout
    assert sample_contact.numero in result.stdout
    for group in sample_contact.groups:
        assert group in result.stdout


def test_list_contacts_json(
    runner: CliRunner,
    mock_client: Mock,
    sample_contact: Contact
) -> None:
    """Test contact listing in JSON format.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_contact: Sample contact fixture.
    """
    mock_client.list_contacts.return_value = [sample_contact]
    
    result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0
    
    import json
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["contact_id"] == str(sample_contact.contact_id)
    assert data[0]["name"] == sample_contact.name
    assert data[0]["numero"] == sample_contact.numero


def test_add_contact_success(
    runner: CliRunner,
    mock_client: Mock,
    sample_contact: Contact
) -> None:
    """Test successful contact addition.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_contact: Sample contact fixture.
    """
    mock_client.create_contact.return_value = sample_contact
    
    result = runner.invoke(app, [
        "add",
        "--numero", "623000000",
        "--name", "John Doe",
        "--groups", "VIP",
        "--groups", "Customers"
    ])
    
    assert result.exit_code == 0
    assert "Contact added successfully!" in result.stdout
    assert str(sample_contact.contact_id) in result.stdout
    assert sample_contact.name in result.stdout
    assert sample_contact.numero in result.stdout


def test_add_contact_without_name(
    runner: CliRunner,
    mock_client: Mock,
    sample_contact: Contact
) -> None:
    """Test adding contact without name.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_contact: Sample contact fixture.
    """
    contact_without_name = Contact(
        contact_id=sample_contact.contact_id,
        numero="623000000",
        created_at=sample_contact.created_at,
        groups=[]
    )
    mock_client.create_contact.return_value = contact_without_name
    
    result = runner.invoke(app, [
        "add",
        "--numero", "623000000"
    ])
    
    assert result.exit_code == 0
    assert "Contact added successfully!" in result.stdout
    assert "N/A" in result.stdout


def test_error_handling(runner: CliRunner, mock_client: Mock) -> None:
    """Test error handling in commands.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.list_contacts.side_effect = HTTPStatusError(
        "Unauthorized",
        request=Mock(),
        response=Response(401, json={"detail": "Invalid credentials"})
    )
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 1
    assert "Error: Invalid credentials" in result.stdout