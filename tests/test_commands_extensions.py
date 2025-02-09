"""Tests for extension management commands."""

from datetime import datetime
from unittest.mock import patch, Mock
from uuid import UUID
from pathlib import Path
import json
import respx

import pytest
from typer.testing import CliRunner
from httpx import HTTPStatusError, Response

from src.commands.extensions import app
from src.core.types import Extension, ExtensionAction, AuthType
from src.config.settings import ConfigManager, Credentials


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
    with patch("src.commands.extensions._get_client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_extension() -> Extension:
    """Create a sample extension for testing.

    Returns:
        Sample extension instance.
    """
    return Extension(
        extensionid="12345678-1234-5678-1234-567812345678",
        name="Test Extension",
        description="A test extension",
        base_api_url="https://api.test.com",
        auth_type=AuthType.API_KEY,
        is_paid=False,
        is_approved=True,
        is_published=True,
        documentation_url="https://docs.test.com",
        website_url="https://test.com",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        url="https://api.nimbasms.com/v1/extensions/12345678"
    )


def test_list_extensions_empty(runner: CliRunner, mock_client: Mock) -> None:
    """Test listing extensions when none exist.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.list_extensions.return_value = []
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No extensions found" in result.stdout


def test_list_extensions_table(
    runner: CliRunner,
    mock_client: Mock,
    sample_extension: Extension
) -> None:
    """Test listing extensions in table format.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_extension: Sample extension fixture.
    """
    mock_client.list_extensions.return_value = [sample_extension]
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    
    # Check that key information is present in the output
    assert "Extension 1:" in result.stdout
    assert f"Name: {sample_extension.name}" in result.stdout
    assert f"Description: {sample_extension.description}" in result.stdout
    assert f"Auth Type: {sample_extension.auth_type.value}" in result.stdout
    assert sample_extension.auth_type.value in result.stdout


def test_list_extensions_json(
    runner: CliRunner,
    mock_client: Mock,
    sample_extension: Extension
) -> None:
    """Test listing extensions in JSON format.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_extension: Sample extension fixture.
    """
    mock_client.list_extensions.return_value = [sample_extension]
    
    result = runner.invoke(app, ["list", "--output", "json"])
    print(result.stdout)
    assert result.exit_code == 0
    
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["name"] == sample_extension.name
    assert data[0]["extensionid"] == str(sample_extension.extensionid)


def test_get_extension(
    runner: CliRunner,
    mock_client: Mock,
    sample_extension: Extension
) -> None:
    """Test getting extension details.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_extension: Sample extension fixture.
    """
    mock_client.get_extension.return_value = sample_extension
    
    result = runner.invoke(app, ["get", str(sample_extension.extensionid)])
    assert result.exit_code == 0
    assert f"Name: {sample_extension.name}" in result.stdout
    assert f"Description: {sample_extension.description}" in result.stdout


def test_get_extension_json(
    runner: CliRunner,
    mock_client: Mock,
    sample_extension: Extension
) -> None:
    """Test getting extension details in JSON format.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_extension: Sample extension fixture.
    """
    mock_client.get_extension.return_value = sample_extension
    
    result = runner.invoke(app, ["get", str(sample_extension.extensionid), "--output", "json"])
    print(result.stdout)
    assert result.exit_code == 0
    
    data = json.loads(result.stdout)
    assert data["name"] == sample_extension.name
    assert data["extensionid"] == str(sample_extension.extensionid)


def test_create_extension(runner: CliRunner, mock_client: Mock) -> None:
    """Test creating a new extension.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    test_id = UUID("12345678-1234-5678-1234-567812345678")
    mock_client.create_extension.return_value = Extension(
        extensionid=test_id,
        name="New Extension",
        category='payments',
        description="A new test extension",
        base_api_url="https://api.test.com",
        auth_type=AuthType.NONE,
        is_paid=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        url="https://api.nimbasms.com/v1/extensions/12345678"
    )
    
    result = runner.invoke(app, [
        "create",
        "--name", "New Extension",
        "--category", "payments",
        "--description", "A new test extension",
        "--base-api-url", "https://api.test.com",
    ])
    
    assert result.exit_code == 0
    assert "Extension created successfully" in result.stdout
    assert str(test_id) in result.stdout


def test_update_extension(
    runner: CliRunner,
    mock_client: Mock,
    sample_extension: Extension
) -> None:
    """Test updating an extension.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
        sample_extension: Sample extension fixture.
    """
    mock_client.update_extension.return_value = sample_extension
    
    result = runner.invoke(app, [
        "update",
        str(sample_extension.extensionid),
        "--name", "Updated Name",
        "--description", "Updated description"
    ])
    
    assert result.exit_code == 0
    assert "Extension updated successfully" in result.stdout
    mock_client.update_extension.assert_called_once()


def test_update_extension_no_changes(
    runner: CliRunner,
    mock_client: Mock
) -> None:
    """Test updating an extension with no changes.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    result = runner.invoke(app, [
        "update",
        "12345678-1234-5678-1234-567812345678"
    ])
    
    assert result.exit_code == 0
    assert "No updates provided" in result.stdout
    mock_client.update_extension.assert_not_called()


def test_error_handling(runner: CliRunner, mock_client: Mock) -> None:
    """Test error handling in commands.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.list_extensions.side_effect = HTTPStatusError(
        "Unauthorized",
        request=Mock(),
        response=Response(401, json={"detail": "Invalid credentials"})
    )
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 1
    assert "Error: Invalid credentials" in result.stdout


def test_upload_logo_file_not_found(runner: CliRunner, mock_client: Mock) -> None:
    """Test uploading non-existent logo file.

    Args:
        runner: CLI runner fixture.
        mock_client: Mock API client fixture.
    """
    mock_client.upload_logo.side_effect = FileNotFoundError("Logo file not found")
    
    result = runner.invoke(app, [
        "upload-logo",
        "12345678-1234-5678-1234-567812345678",
        "non_existent_logo.png"
    ])
    
    assert result.exit_code == 1
    assert "Logo file not found" in result.stdout


def test_publish_extension(runner: CliRunner, mock_client: Mock) -> None:
    """Test publishing an extension."""
    mock_client.publish_action.return_value = {"status": "OK"}
    
    result = runner.invoke(app, [
        "publish",
        "12345678-1234-5678-1234-567812345678"
    ])
    
    assert result.exit_code == 0
    assert "Extension published successfully!" in result.stdout
    mock_client.publish_action.assert_called_once()


def test_missing_credentials(runner: CliRunner) -> None:
    """Test behavior when credentials are missing."""
    from src.config.settings import Credentials
    
    with patch("src.commands.extensions.settings.load_credentials") as mock_creds:
        mock_creds.return_value = Credentials(service_id=None, secret_token=None)
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 1
        assert "Error: API credentials not configured" in result.stdout


def test_http_error_details(runner: CliRunner, mock_client: Mock) -> None:
    """Test HTTP error with specific details."""
    mock_client.list_extensions.side_effect = HTTPStatusError(
        "Bad Request",
        request=Mock(),
        response=Response(400, json={"detail": "Invalid request parameters"})
    )
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 1
    assert "Error: Invalid request parameters" in result.stdout


def test_update_extension_with_all_fields(
    runner: CliRunner,
    mock_client: Mock,
    sample_extension: Extension
) -> None:
    """Test updating all possible fields of an extension."""
    mock_client.update_extension.return_value = sample_extension
    
    result = runner.invoke(app, [
        "update",
        str(sample_extension.extensionid),
        "--name", "Updated Name",
        "--description", "Updated description",
        "--base-api-url", "https://new-api.test.com",
        "--docs-url", "https://new-docs.test.com",
        "--website-url", "https://new-website.test.com"
    ])
    
    assert result.exit_code == 0
    assert "Extension updated successfully!" in result.stdout
    mock_client.update_extension.assert_called_once()


def test_save_credentials_new_file(tmp_path: Path) -> None:
    """Test saving credentials to a new config file."""
    config = ConfigManager(config_dir=tmp_path)
    config.save_credentials("test_id", "test_token")
    
    saved = config.load_credentials()
    assert saved.service_id == "test_id"
    assert saved.secret_token == "test_token"


def test_save_credentials_update_existing(tmp_path: Path) -> None:
    """Test updating existing credentials."""
    config = ConfigManager(config_dir=tmp_path)
    config.save_credentials("test_id", "test_token")
    config.save_credentials(service_id="new_id")
    
    saved = config.load_credentials()
    assert saved.service_id == "new_id"
    assert saved.secret_token == "test_token"


def test_load_credentials_invalid_json(tmp_path: Path) -> None:
    """Test loading credentials from invalid JSON file."""
    config = ConfigManager(config_dir=tmp_path)
    config.config_file.parent.mkdir(parents=True, exist_ok=True)
    config.config_file.write_text("invalid json")
    
    creds = config.load_credentials()
    assert creds.service_id is None
    assert creds.secret_token is None


def test_create_extension_oauth2(runner: CliRunner, mock_client: Mock) -> None:
    """Test creating extension with OAuth2 config."""
    mock_client.create_extension.return_value = Extension(
        extensionid=UUID("12345678-1234-5678-1234-567812345678"),
        name="OAuth2 Test",
        category="crm",
        auth_type=AuthType.OAUTH2,
        description="Test OAuth2 extension",
        base_api_url="https://api.test.com",
        is_paid=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        url="https://api.nimbasms.com/v1/extensions/12345678"
    )
    
    result = runner.invoke(app, [
        "create",
        "--name", "OAuth2 Test",
        "--category", "crm",
        "--description", "Test OAuth2 extension",
        "--base-api-url", "https://api.test.com",
        "--auth-type", "oauth2"
    ])
    
    assert result.exit_code == 0
    assert "Extension created successfully!" in result.stdout
    mock_client.create_extension.assert_called_once()


def test_list_extensions_pagination(runner: CliRunner, mock_client: Mock) -> None:
    """Test extension listing with pagination."""
    ext1 = Extension(
        extensionid=UUID("12345678-1234-5678-1234-567812345678"),
        name="Test 1",
        description="First test extension",
        base_api_url="https://api.test1.com",
        auth_type=AuthType.NONE,
        is_paid=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        url="https://api.nimbasms.com/v1/extensions/1"
    )
    ext2 = Extension(
        extensionid=UUID("87654321-4321-8765-4321-876543210987"),
        name="Test 2",
        description="Second test extension",
        base_api_url="https://api.test2.com",
        auth_type=AuthType.API_KEY,
        is_paid=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        url="https://api.nimbasms.com/v1/extensions/2"
    )
    
    mock_client.list_extensions.return_value = [ext1, ext2]
    
    result = runner.invoke(app, ["list", "--limit", "2", "--offset", "0"])
    assert result.exit_code == 0
    assert ext1.name in result.stdout
    assert ext2.name in result.stdout
    mock_client.list_extensions.assert_called_once_with(limit=2, offset=0)