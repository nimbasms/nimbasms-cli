"""Data models for Nimba SMS API."""

from enum import Enum
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class Account(BaseModel):
    """Account information model."""
    sid: str
    balance: int
    webhook_url: Optional[str] = None


class AuthType(str, Enum):
    """Authentication types for extensions."""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"


class HTTPMethod(str, Enum):
    """HTTP methods for extension actions."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class OAuth2Config(BaseModel):
    """OAuth2 configuration model."""
    client_id: str
    client_secret: str
    authorization_url: HttpUrl
    token_url: HttpUrl
    scope_separator: str
    redirect_url: HttpUrl
    available_scopes: Dict[str, str] = Field(description='{"scope_name": "description"}')
    required_scopes: List[str] = Field(description='["scope1", "scope2"]')


class Extension(BaseModel):
    """Extension model."""
    extensionid: UUID = Field(description="Extension identifier")
    name: str
    description: str = Field(max_length=400)
    logo: Optional[HttpUrl] = None
    base_api_url: HttpUrl
    auth_type: AuthType
    is_paid: bool = Field(description="Indicates if the extension is paid")
    is_approved: bool = Field(default=False, description="Indicates if extension is approved")
    is_published: bool = Field(default=False, description="Indicates if extension is published")
    documentation_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None
    created_at: datetime
    updated_at: datetime
    url: HttpUrl


class CreateExtension(BaseModel):
    """Model for creating a new extension."""
    name: str = Field(max_length=30)
    description: str = Field(max_length=400)
    base_api_url: HttpUrl
    auth_type: AuthType
    is_paid: bool
    documentation_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None
    oauth2_config: Optional[OAuth2Config] = None


class ExtensionAction(BaseModel):
    """Extension action model."""
    actionid: UUID
    name: str = Field(max_length=100)
    method: HTTPMethod
    endpoint: str = Field(max_length=255)
    description: str = Field(max_length=200)
    required_params: Dict[str, Any] = Field(default_factory=dict)
    optional_params: Dict[str, Any] = Field(default_factory=dict)
    response_format: Dict[str, Any] = Field(default_factory=dict)


class PricingPlan(BaseModel):
    """Pricing plan model."""
    pricingplanid: Optional[UUID] = None
    name: str = Field(max_length=100)
    price: str  # Decimal as string
    billing_period: Literal["monthly", "yearly"] = Field(description="Billing period (monthly/yearly)")
    features: Dict[str, Any]


class ExtensionPublish(BaseModel):
    """Extension publish status model."""
    is_published: bool
    status: Optional[str] = Field(default="OK")


class Contact(BaseModel):
    """Contact model."""
    contact_id: UUID = Field(description="Contact identifier")
    name: Optional[str] = Field(None, max_length=400)
    numero: str = Field(..., max_length=128)
    created_at: int
    groups: List[str] = Field(default_factory=list)


class CreateContact(BaseModel):
    """Model for creating a new contact."""
    name: Optional[str] = Field(None, max_length=400)
    numero: str = Field(..., max_length=128)
    groups: List[str] = Field(default_factory=list)


class Groupe(BaseModel):
    """Group model."""
    groupe_id: UUID = Field(description="Group identifier")
    name: str = Field(..., max_length=100)
    added_at: int
    total_contact: int


class MessageStatus(str, Enum):
    """Message status enum."""
    PENDING = "pending"
    SENT = "sent"
    FAILURE = "failure"
    NOT_AVAILABLE = "not_available"
    RECEIVED = "received"
    TOSEND = "tosend"


class DeliveryMessage(BaseModel):
    """Delivery message status model."""
    id: UUID
    contact: str
    status: MessageStatus


class Message(BaseModel):
    """Message model."""
    messageid: UUID = Field(description="Message identifier")
    sender_name: str = Field(..., max_length=11)
    message: str = Field(..., max_length=665)
    status: MessageStatus
    sent_at: int
    numbers: List[DeliveryMessage] = Field(default_factory=list)


class CreateMessage(BaseModel):
    """Model for creating a new message."""
    sender_name: str = Field(..., max_length=11)
    to: List[str] = Field(..., min_length=1, max_length=10)
    message: str = Field(..., max_length=665)


class MessageResponse(BaseModel):
    """Message creation response model."""
    messageid: UUID
    url: HttpUrl


class SenderName(BaseModel):
    """SenderName model."""
    sendername_id: UUID
    name: str
    status: Literal["pending", "refused", "accepted"]
    added_at: int


class VerificationStatus(str, Enum):
    """Verification status enum."""
    PENDING = "pending"
    SENT = "sent"
    EXPIRED = "expired"
    FAILURE = "failure"
    RECEIVED = "received"
    TOO_MANY_ATTEMPTS = "too_many_attempts"
    APPROVED = "approved"


class RequestVerification(BaseModel):
    """Verification request model."""
    verificationid: UUID = Field(default=UUID("c195e2f8-bca2-4173-886d-4820fd578d21"))
    to: str = Field(..., max_length=128)
    message: Optional[str] = Field(None, max_length=153)
    sender_name: Optional[str] = Field(None, max_length=11)
    expiry_time: Optional[int] = Field(None, ge=5, le=30)
    attempts: Optional[int] = Field(None, ge=3, le=10)
    code: Optional[str] = None
    code_length: Optional[int] = Field(None, ge=4, le=8)
    url: Optional[HttpUrl] = None


class RequestVerificationResponse(BaseModel):
    """Verification request model."""
    verificationid: UUID = Field(default=UUID("c195e2f8-bca2-4173-886d-4820fd578d21"))
    code: Optional[str] = None
    url: Optional[HttpUrl] = None


class CheckVerification(BaseModel):
    """Verification check model."""
    code: int = Field(..., ge=1000, le=999999)
    status: VerificationStatus = Field(None)