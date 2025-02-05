"""Tests for the Nimba SMS API client.

This module contains test cases for the API client and its related functionality.
"""

import pytest
import httpx
import respx

from src.core.api import APIClient, Account


@pytest.fixture
def api_client() -> APIClient:
    """Create an API client for testing.

    Returns:
        A configured API client instance.
    """
    return APIClient("test_id", "test_token", "https://api.nimbasms.com/v1")


@pytest.fixture
def mock_api():
    """Create a mock API using respx.

    Yields:
        A mock context that can be used to simulate API responses.
    """
    with respx.mock(assert_all_called=False) as respx_mock:
        yield respx_mock


def test_get_account_success(api_client: APIClient, mock_api) -> None:
    """Test successful account information retrieval.

    Args:
        api_client: The API client fixture.
        mock_api: The mock API fixture.
    """
    mock_response = {
        "sid": "test123",
        "balance": 1000,
        "webhook_url": "https://example.com/webhook",
    }

    mock_api.get("https://api.nimbasms.com/v1/accounts").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    account = api_client.get_account()
    assert isinstance(account, Account)
    assert account.sid == "test123"
    assert account.balance == 1000
    assert account.webhook_url == "https://example.com/webhook"


def test_get_account_unauthorized(api_client: APIClient, mock_api) -> None:
    """Test account retrieval with invalid credentials.

    Args:
        api_client: The API client fixture.
        mock_api: The mock API fixture.
    """
    mock_api.get("https://api.nimbasms.com/v1/accounts").mock(
        return_value=httpx.Response(
            401, json={"detail": "Authentication credentials not provided."}
        )
    )

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        api_client.get_account()

    assert exc_info.value.response.status_code == 401


def test_get_account_server_error(api_client: APIClient, mock_api) -> None:
    """Test account retrieval when server error occurs.

    Args:
        api_client: The API client fixture.
        mock_api: The mock API fixture.
    """
    mock_api.get("https://api.nimbasms.com/v1/accounts").mock(
        return_value=httpx.Response(500, json={"detail": "Internal server error"})
    )

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        api_client.get_account()

    assert exc_info.value.response.status_code == 500