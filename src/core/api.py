"""Core API client for Nimba SMS API."""

from typing import Optional, List
from uuid import UUID
from pathlib import Path

import httpx
from typing_extensions import Annotated

from .types import (
    Account, Extension, CreateExtension, ExtensionAction,
    PricingPlan, ExtensionPublish
)


class APIClient:
    """Main API client for Nimba SMS."""

    def __init__(
        self,
        service_id: str,
        secret_token: str,
        base_url: str = "https://api.test.nimbasms.com/v1",
    ) -> None:
        """Initialize API client.

        Args:
            service_id: The service identifier.
            secret_token: The authentication token.
            base_url: Base URL for the API (default: production URL).
        """
        self.base_url = base_url
        self.auth = httpx.BasicAuth(service_id, secret_token)
        self.client = httpx.Client()

    def get_account(self) -> Account:
        """Retrieve account information.

        Returns:
            Account information including balance and webhook URL.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        response = self.client.get(f"{self.base_url}/accounts", auth=self.auth)
        response.raise_for_status()
        return Account(**response.json())

    # Extension management
    def list_extensions(self, limit: int = 10, offset: int = 0) -> List[Extension]:
        """List available extensions.
        
        Args:
            limit: Maximum number of extensions to return.
            offset: Number of extensions to skip.
        
        Returns:
            List of extensions.
        """
        response = self.client.get(
            f"{self.base_url}/extensions",
            params={"limit": limit, "offset": offset},
            auth=self.auth
        )
        response.raise_for_status()
        data = response.json()
        return [Extension(**ext) for ext in data["results"]]

    def create_extension(self, data: CreateExtension) -> Extension:
        """Create a new extension.
        
        Args:
            data: Extension creation data.
        
        Returns:
            Created extension.
        """
        response = self.client.post(
            f"{self.base_url}/extensions",
            json=data.model_dump(exclude_none=True),
            auth=self.auth
        )
        response.raise_for_status()
        return Extension(**response.json())

    def get_extension(self, extension_id: UUID) -> Extension:
        """Get extension details.
        
        Args:
            extension_id: Extension identifier.
        
        Returns:
            Extension details.
        """
        response = self.client.get(
            f"{self.base_url}/extensions/{extension_id}",
            auth=self.auth
        )
        response.raise_for_status()
        return Extension(**response.json())

    def update_extension(self, extension_id: UUID, data: dict) -> Extension:
        """Update an extension.
        
        Args:
            extension_id: Extension identifier.
            data: Fields to update.
        
        Returns:
            Updated extension.
        """
        response = self.client.patch(
            f"{self.base_url}/extensions/{extension_id}",
            json=data,
            auth=self.auth
        )
        response.raise_for_status()
        return Extension(**response.json())

    def upload_logo(self, extension_id: UUID, logo_path: Path) -> Extension:
        """Upload extension logo.
        
        Args:
            extension_id: Extension identifier.
            logo_path: Path to logo image file.
        
        Returns:
            Updated extension.
        
        Raises:
            FileNotFoundError: If logo file doesn't exist.
            ValueError: If logo file is invalid.
        """
        if not logo_path.exists():
            raise FileNotFoundError(f"Logo file not found: {logo_path}")

        files = {"logo": ("logo.png", logo_path.open("rb"), "image/png")}
        response = self.client.patch(
            f"{self.base_url}/extensions/{extension_id}/logo",
            files=files,
            auth=self.auth
        )
        response.raise_for_status()
        return Extension(**response.json())

    # Extension actions
    def list_actions(
        self, extension_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[ExtensionAction]:
        """List extension actions.
        
        Args:
            extension_id: Extension identifier.
            limit: Maximum number of actions to return.
            offset: Number of actions to skip.
        
        Returns:
            List of extension actions.
        """
        response = self.client.get(
            f"{self.base_url}/extensions/{extension_id}/actions",
            params={"limit": limit, "offset": offset},
            auth=self.auth
        )
        response.raise_for_status()
        data = response.json()
        return [ExtensionAction(**action) for action in data["results"]]

    def create_action(
        self, extension_id: UUID, data: ExtensionAction
    ) -> ExtensionAction:
        """Create a new action.
        
        Args:
            extension_id: Extension identifier.
            data: Action data.
        
        Returns:
            Created action.
        """
        response = self.client.post(
            f"{self.base_url}/extensions/{extension_id}/actions",
            json=data.model_dump(exclude_none=True),
            auth=self.auth
        )
        response.raise_for_status()
        return ExtensionAction(**response.json())

    def update_action(
        self, extension_id: UUID, action_id: UUID, data: dict
    ) -> ExtensionAction:
        """Update an action.
        
        Args:
            extension_id: Extension identifier.
            action_id: Action identifier.
            data: Fields to update.
        
        Returns:
            Updated action.
        """
        response = self.client.patch(
            f"{self.base_url}/extensions/{extension_id}/actions/{action_id}",
            json=data,
            auth=self.auth
        )
        response.raise_for_status()
        return ExtensionAction(**response.json())

    def delete_action(self, extension_id: UUID, action_id: UUID) -> None:
        """Delete an action.
        
        Args:
            extension_id: Extension identifier.
            action_id: Action identifier.
        """
        response = self.client.delete(
            f"{self.base_url}/extensions/{extension_id}/actions/{action_id}",
            auth=self.auth
        )
        response.raise_for_status()

    def publish_action(
        self, extension_id: UUID, action_id: UUID
    ) -> ExtensionPublish:
        """Publish an action.
        
        Args:
            extension_id: Extension identifier.
            action_id: Action identifier.
        
        Returns:
            Publish status.
        """
        response = self.client.post(
            f"{self.base_url}/extensions/{extension_id}/actions/{action_id}/publish",
            auth=self.auth
        )
        response.raise_for_status()
        return ExtensionPublish(**response.json())


    def list_messages(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None,
        sent_at__gte: Optional[str] = None,
        sent_at__lte: Optional[str] = None,
    ) -> List[Message]:
        """List messages with optional filtering.
        
        Args:
            limit: Maximum number of messages to return.
            offset: Number of messages to skip.
            status: Filter by message status.
            sent_at__gte: Filter by sent date (greater than or equal).
            sent_at__lte: Filter by sent date (less than or equal).
        
        Returns:
            List of messages matching the criteria.
        """
        params = {
            "limit": limit,
            "offset": offset,
            **({"status": status} if status else {}),
            **({"sent_at__gte": sent_at__gte} if sent_at__gte else {}),
            **({"sent_at__lte": sent_at__lte} if sent_at__lte else {}),
        }
        response = self.client.get(
            f"{self.base_url}/messages",
            params=params,
            auth=self.auth
        )
        response.raise_for_status()
        data = response.json()
        return [Message(**msg) for msg in data["results"]]

    def send_message(self, message: CreateMessage) -> MessageResponse:
        """Send a new message.
        
        Args:
            message: Message creation data.
        
        Returns:
            Message response with ID and status URL.
        """
        response = self.client.post(
            f"{self.base_url}/messages",
            json=message.model_dump(exclude_none=True),
            auth=self.auth
        )
        response.raise_for_status()
        return MessageResponse(**response.json())

    def get_message(self, message_id: UUID) -> Message:
        """Get message details.
        
        Args:
            message_id: Message identifier.
        
        Returns:
            Message details including delivery status.
        """
        response = self.client.get(
            f"{self.base_url}/messages/{message_id}",
            auth=self.auth
        )
        response.raise_for_status()
        return Message(**response.json())

    # Contacts
    def list_contacts(self, limit: int = 10, offset: int = 0) -> List[Contact]:
        """List contacts.
        
        Args:
            limit: Maximum number of contacts to return.
            offset: Number of contacts to skip.
        
        Returns:
            List of contacts.
        """
        response = self.client.get(
            f"{self.base_url}/contacts",
            params={"limit": limit, "offset": offset},
            auth=self.auth
        )
        response.raise_for_status()
        data = response.json()
        return [Contact(**contact) for contact in data]

    def create_contact(self, contact: CreateContact) -> Contact:
        """Create a new contact.
        
        Args:
            contact: Contact creation data.
        
        Returns:
            Created contact details.
        """
        response = self.client.post(
            f"{self.base_url}/contacts",
            json=contact.model_dump(exclude_none=True),
            auth=self.auth
        )
        response.raise_for_status()
        return Contact(**response.json())

    # Groups
    def list_groups(self, limit: int = 10, offset: int = 0) -> List[Groupe]:
        """List groups.
        
        Args:
            limit: Maximum number of groups to return.
            offset: Number of groups to skip.
        
        Returns:
            List of groups.
        """
        response = self.client.get(
            f"{self.base_url}/groups",
            params={"limit": limit, "offset": offset},
            auth=self.auth
        )
        response.raise_for_status()
        data = response.json()
        return [Groupe(**group) for group in data["results"]]

    # Sender Names
    def list_sender_names(self, limit: int = 10, offset: int = 0) -> List[SenderName]:
        """List sender names.
        
        Args:
            limit: Maximum number of sender names to return.
            offset: Number of sender names to skip.
        
        Returns:
            List of sender names.
        """
        response = self.client.get(
            f"{self.base_url}/sendernames",
            params={"limit": limit, "offset": offset},
            auth=self.auth
        )
        response.raise_for_status()
        data = response.json()
        return [SenderName(**name) for name in data["results"]]

    # Verifications
    def create_verification(self, verification: RequestVerification) -> RequestVerification:
        """Create a new verification request.
        
        Args:
            verification: Verification request data.
        
        Returns:
            Created verification request.
        """
        response = self.client.post(
            f"{self.base_url}/verifications",
            json=verification.model_dump(exclude_none=True),
            auth=self.auth
        )
        response.raise_for_status()
        return RequestVerification(**response.json())

    def check_verification(
        self, verification_id: UUID, verification: CheckVerification
    ) -> CheckVerification:
        """Check a verification code.
        
        Args:
            verification_id: Verification request identifier.
            verification: Verification check data.
        
        Returns:
            Verification check result.
        """
        response = self.client.patch(
            f"{self.base_url}/verifications/{verification_id}",
            json=verification.model_dump(exclude_none=True),
            auth=self.auth
        )
        response.raise_for_status()
        return CheckVerification(**response.json())