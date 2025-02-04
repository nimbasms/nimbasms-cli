import io
import uuid
from pathlib import Path

import httpx
import pytest

from src.core.api import APIClient

class DummyModel:
    def __init__(self, data):
        self.data = data

    def model_dump(self, exclude_none=False, mode='json'):
        return self.data

ACCOUNT_DATA = {
    "sid": "dummy_sid",
    "balance": 100,
    "webhook_url": "http://example.com/webhook"
}

EXTENSION_DATA = {
    "extensionid": "00000000-0000-0000-0000-000000000000",
    "name": "Extension 1",
    "description": "dummy description",
    "logo": "http://dummy/logo.png",
    "base_api_url": "http://dummy/api",
    "auth_type": "none",
    "is_paid": False,
    "is_approved": False,
    "is_published": False,
    "documentation_url": "http://dummy/docs",
    "website_url": "http://dummy/website",
    "created_at": "2020-01-01T00:00:00",
    "updated_at": "2020-01-01T00:00:00",
    "url": "http://dummy/url"
}

EXTENSION_ACTION_DATA = {
    "actionid": "00000000-0000-0000-0000-000000000001",
    "name": "Action 1",
    "method": "GET",
    "endpoint": "/dummy",
    "description": "dummy action",
    "required_params": {},
    "optional_params": {},
    "response_format": {}
}

EXTENSION_PUBLISH_DATA = {
    "is_published": True,
    "status": "OK"
}

MESSAGE_DATA = {
    "messageid": "00000000-0000-0000-0000-000000000002",
    "sender_name": "SENDER",
    "message": "Hello World",
    "status": "sent",
    "sent_at": 1234567890,
    "numbers": []
}

MESSAGE_RESPONSE_DATA = {
    "messageid": "00000000-0000-0000-0000-000000000003",
    "url": "http://dummy/message"
}

CONTACT_DATA = {
    "contact_id": "00000000-0000-0000-0000-000000000004",
    "name": "Contact 1",
    "numero": "123456789",
    "created_at": 1234567890,
    "groups": []
}

GROUP_DATA = {
    "groupe_id": "00000000-0000-0000-0000-000000000005",
    "name": "Groupe 1",
    "added_at": 1234567890,
    "total_contact": 0
}

SENDER_NAME_DATA = {
    "sendername_id": "00000000-0000-0000-0000-000000000006",
    "name": "SenderName 1",
    "status": "accepted",
    "added_at": 1234567890
}

REQUEST_VERIFICATION_DATA = {
    "verificationid": "c195e2f8-bca2-4173-886d-4820fd578d21",
    "to": "1234567890",
    "message": "dummy message",
    "sender_name": "SENDER",
    "expiry_time": 10,
    "attempts": 3,
    "code": "1234",
    "code_length": 4,
    "url": "http://dummy/verification"
}

CHECK_VERIFICATION_DATA = {
    "code": 1234,
    "status": "approved"
}

def make_response(json_data, status_code=200):
    request = httpx.Request("GET", "http://test")
    return httpx.Response(status_code, json=json_data, request=request)

@pytest.fixture
def client():
    return APIClient("service_id", "secret_token", base_url="http://test.api")

def test_get_account(monkeypatch, client):
    monkeypatch.setattr(
        client.client, "get",
        lambda url, auth=None, params=None: make_response(ACCOUNT_DATA)
    )
    account = client.get_account()
    assert account.sid == ACCOUNT_DATA["sid"]
    assert account.balance == ACCOUNT_DATA["balance"]
    assert account.webhook_url == ACCOUNT_DATA["webhook_url"]

def test_list_extensions(monkeypatch, client):
    monkeypatch.setattr(
        client.client, "get",
        lambda url, auth=None, params=None: make_response({"results": [EXTENSION_DATA]})
    )
    extensions = client.list_extensions(limit=5, offset=2)
    assert isinstance(extensions, list)
    assert len(extensions) == 1
    ext = extensions[0]
    assert str(ext.extensionid) == EXTENSION_DATA["extensionid"]
    assert ext.name == EXTENSION_DATA["name"]

def test_create_extension(monkeypatch, client):
    monkeypatch.setattr(
        client.client, "post",
        lambda url, json, auth=None: make_response(EXTENSION_DATA)
    )
    dummy_extension = DummyModel({
        "name": "New Extension",
        "description": "A new extension",
        "base_api_url": "http://dummy/api",
        "auth_type": "none",
        "is_paid": False
    })
    ext = client.create_extension(dummy_extension)
    assert str(ext.extensionid) == EXTENSION_DATA["extensionid"]
    assert ext.name == EXTENSION_DATA["name"]

def test_get_extension(monkeypatch, client):
    ext_id = uuid.UUID(EXTENSION_DATA["extensionid"])
    monkeypatch.setattr(
        client.client, "get",
        lambda url, auth=None, params=None: make_response(EXTENSION_DATA)
    )
    ext = client.get_extension(ext_id)
    assert str(ext.extensionid) == EXTENSION_DATA["extensionid"]

def test_update_extension(monkeypatch, client):
    ext_id = uuid.UUID(EXTENSION_DATA["extensionid"])
    updated_data = {"name": "Updated Extension"}
    monkeypatch.setattr(
        client.client, "patch",
        lambda url, json, auth=None: make_response(EXTENSION_DATA)
    )
    ext = client.update_extension(ext_id, updated_data)
    assert str(ext.extensionid) == EXTENSION_DATA["extensionid"]

def test_upload_logo(monkeypatch, client, tmp_path):
    logo_file = tmp_path / "logo.png"
    logo_file.write_bytes(b"fake image data")
    ext_id = uuid.UUID(EXTENSION_DATA["extensionid"])
    def fake_patch(url, files, auth=None):
        assert "logo" in files
        filename, fileobj, content_type = files["logo"]
        assert filename == "logo.png"
        assert content_type == "image/png"
        data = fileobj.read()
        assert data == b"fake image data"
        return make_response(EXTENSION_DATA)
    monkeypatch.setattr(client.client, "patch", fake_patch)
    ext = client.upload_logo(ext_id, logo_file)
    assert str(ext.extensionid) == EXTENSION_DATA["extensionid"]

def test_upload_logo_file_not_found(client):
    fake_path = Path("nonexistent_logo.png")
    ext_id = uuid.UUID(EXTENSION_DATA["extensionid"])
    with pytest.raises(FileNotFoundError):
        client.upload_logo(ext_id, fake_path)

def test_list_actions(monkeypatch, client):
    ext_id = uuid.UUID(EXTENSION_DATA["extensionid"])
    monkeypatch.setattr(
        client.client, "get",
        lambda url, auth=None, params=None: make_response({"results": [EXTENSION_ACTION_DATA]})
    )
    actions = client.list_actions(ext_id, limit=3, offset=1)
    assert isinstance(actions, list)
    assert len(actions) == 1
    action = actions[0]
    assert str(action.actionid) == EXTENSION_ACTION_DATA["actionid"]
    assert action.name == EXTENSION_ACTION_DATA["name"]

def test_create_action(monkeypatch, client):
    ext_id = uuid.UUID(EXTENSION_DATA["extensionid"])
    monkeypatch.setattr(
        client.client, "post",
        lambda url, json, auth=None: make_response(EXTENSION_ACTION_DATA)
    )
    dummy_action = DummyModel({"name": "New Action", "method": "GET", "endpoint": "/dummy", "description": "desc"})
    action = client.create_action(ext_id, dummy_action)
    assert str(action.actionid) == EXTENSION_ACTION_DATA["actionid"]

def test_update_action(monkeypatch, client):
    ext_id = uuid.UUID(EXTENSION_DATA["extensionid"])
    action_id = uuid.UUID(EXTENSION_ACTION_DATA["actionid"])
    updated_data = {"name": "Updated Action"}
    monkeypatch.setattr(
        client.client, "patch",
        lambda url, json, auth=None: make_response(EXTENSION_ACTION_DATA)
    )
    action = client.update_action(ext_id, action_id, updated_data)
    assert str(action.actionid) == EXTENSION_ACTION_DATA["actionid"]

def test_delete_action(monkeypatch, client):
    ext_id = uuid.UUID(EXTENSION_DATA["extensionid"])
    action_id = uuid.UUID(EXTENSION_ACTION_DATA["actionid"])
    monkeypatch.setattr(
        client.client, "delete",
        lambda url, auth=None: make_response({}, status_code=200)
    )
    client.delete_action(ext_id, action_id)

def test_publish_action(monkeypatch, client):
    ext_id = uuid.UUID(EXTENSION_DATA["extensionid"])
    action_id = uuid.UUID(EXTENSION_ACTION_DATA["actionid"])
    monkeypatch.setattr(
        client.client, "post",
        lambda url, auth=None: make_response(EXTENSION_PUBLISH_DATA)
    )
    publish = client.publish_action(ext_id, action_id)
    assert publish.is_published is True
    assert publish.status == EXTENSION_PUBLISH_DATA["status"]

def test_list_messages(monkeypatch, client):
    params_expected = {
        "limit": 7,
        "offset": 0,
        "status": "sent",
        "sent_at__gte": "2025-01-01",
        "sent_at__lte": "2025-01-31",
    }
    def fake_get(url, auth=None, params=None):
        for key, value in params_expected.items():
            assert params.get(key) == value
        return make_response({"results": [MESSAGE_DATA]})
    monkeypatch.setattr(client.client, "get", fake_get)
    messages = client.list_messages(
        limit=7,
        offset=0,
        status="sent",
        sent_at__gte="2025-01-01",
        sent_at__lte="2025-01-31",
    )
    assert isinstance(messages, list)
    assert len(messages) == 1
    msg = messages[0]
    assert str(msg.messageid) == MESSAGE_DATA["messageid"]

def test_send_message(monkeypatch, client):
    monkeypatch.setattr(
        client.client, "post",
        lambda url, json, auth=None: make_response(MESSAGE_RESPONSE_DATA)
    )
    dummy_message = DummyModel({"sender_name": "SENDER", "to": ["123456789"], "message": "Hello"})
    msg_resp = client.send_message(dummy_message)
    assert str(msg_resp.messageid) == MESSAGE_RESPONSE_DATA["messageid"]
    assert str(msg_resp.url) == MESSAGE_RESPONSE_DATA["url"]

def test_get_message(monkeypatch, client):
    msg_id = uuid.UUID(MESSAGE_DATA["messageid"])
    monkeypatch.setattr(
        client.client, "get",
        lambda url, auth=None, params=None: make_response(MESSAGE_DATA)
    )
    msg = client.get_message(msg_id)
    assert str(msg.messageid) == MESSAGE_DATA["messageid"]

def test_list_contacts(monkeypatch, client):
    monkeypatch.setattr(
        client.client, "get",
        lambda url, auth=None, params=None: make_response({"results": [CONTACT_DATA]})
    )
    contacts = client.list_contacts(limit=4, offset=0)
    assert isinstance(contacts, list)
    assert len(contacts) == 1
    contact = contacts[0]
    assert str(contact.contact_id) == CONTACT_DATA["contact_id"]

def test_create_contact(monkeypatch, client):
    monkeypatch.setattr(
        client.client, "post",
        lambda url, json, auth=None: make_response(CONTACT_DATA)
    )
    dummy_contact = DummyModel({"numero": "123456789"})
    contact = client.create_contact(dummy_contact)
    assert str(contact.contact_id) == CONTACT_DATA["contact_id"]

def test_list_groups(monkeypatch, client):
    monkeypatch.setattr(
        client.client, "get",
        lambda url, auth=None, params=None: make_response({"results": [GROUP_DATA]})
    )
    groups = client.list_groups(limit=2, offset=0)
    assert isinstance(groups, list)
    assert len(groups) == 1
    group = groups[0]
    assert str(group.groupe_id) == GROUP_DATA["groupe_id"]

def test_list_sender_names(monkeypatch, client):
    monkeypatch.setattr(
        client.client, "get",
        lambda url, auth=None, params=None: make_response({"results": [SENDER_NAME_DATA]})
    )
    senders = client.list_sender_names(limit=3, offset=0)
    assert isinstance(senders, list)
    assert len(senders) == 1
    sender = senders[0]
    assert str(sender.sendername_id) == SENDER_NAME_DATA["sendername_id"]

def test_create_verification(monkeypatch, client):
    monkeypatch.setattr(
        client.client, "post",
        lambda url, json, auth=None: make_response(REQUEST_VERIFICATION_DATA)
    )
    dummy_verification = DummyModel({"to": "1234567890", "code": "1234"})
    verification = client.create_verification(dummy_verification)
    assert str(verification.verificationid) == REQUEST_VERIFICATION_DATA["verificationid"]

def test_check_verification(monkeypatch, client):
    verification_id = uuid.UUID(REQUEST_VERIFICATION_DATA["verificationid"])
    monkeypatch.setattr(
        client.client, "patch",
        lambda url, json, auth=None: make_response(CHECK_VERIFICATION_DATA)
    )
    dummy_check = DummyModel({"code": 1234})
    result = client.check_verification(verification_id, dummy_check)
    assert result.code == CHECK_VERIFICATION_DATA["code"]
    assert result.status == CHECK_VERIFICATION_DATA["status"]
