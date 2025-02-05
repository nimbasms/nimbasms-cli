"""Tests for group management commands."""

from datetime import datetime
from unittest.mock import patch, Mock
from uuid import UUID

import pytest
from typer.testing import CliRunner
from httpx import HTTPStatusError, Response

from src.commands.groups import app
from src.core.types import Groupe


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
    with patch("src.commands.groups._get_client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_group() -> Groupe:
    """Create a sample group for testing.

    Returns:
        Sample group instance.
    """
    return Groupe(
        groupe_id=UUID("12345678-1234-5678-1234-567812345678"),
        name="Test Group",
        added_at=int(datetime.now().timestamp()),  # Timestamp Unix au lieu de string
        total_contact=42
    )


def test_list_groups_empty(runner: CliRunner, mock_client: Mock) -> None:
    """Test listing groups when none exist.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.list_groups.return_value = []
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No groups found" in result.stdout


def test_list_groups_table(
    runner: CliRunner,
    mock_client: Mock,
    sample_group: Groupe
) -> None:
    """Test listing groups in table format.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_group: Sample group fixture.
    """
    mock_client.list_groups.return_value = [sample_group]
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    # On vérifie seulement le début de l'ID
    assert str(sample_group.groupe_id)[:8] in result.stdout
    assert sample_group.name in result.stdout
    assert str(sample_group.total_contact) in result.stdout


def test_list_groups_json(
    runner: CliRunner,
    mock_client: Mock,
    sample_group: Groupe
) -> None:
    """Test listing groups in JSON format.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_group: Sample group fixture.
    """
    mock_client.list_groups.return_value = [sample_group]
    
    result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0
    
    import json
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["groupe_id"] == str(sample_group.groupe_id)
    assert data[0]["name"] == sample_group.name
    assert data[0]["total_contact"] == sample_group.total_contact


def test_error_handling(runner: CliRunner, mock_client: Mock) -> None:
    """Test error handling in commands.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.list_groups.side_effect = HTTPStatusError(
        "Unauthorized",
        request=Mock(),
        response=Response(401, json={"detail": "Invalid credentials"})
    )
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 1
    assert "Error: Invalid credentials" in result.stdout