from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class PackageTier(str, Enum):
    """Enumeration of supported package tiers."""
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


class UserPublic(BaseModel):
    """Public-facing user model returned by APIs."""
    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User email")
    package_tier: PackageTier = Field(..., description="User's subscription package")


class SignupRequest(BaseModel):
    """Signup input payload."""
    email: EmailStr = Field(..., description="Email for account signup")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    package_tier: Optional[PackageTier] = Field(None, description="Optional package tier; defaults to 'free' if omitted")


class LoginRequest(BaseModel):
    """Login input payload."""
    email: EmailStr = Field(..., description="Email for account login")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """JWT token response model."""
    access_token: str = Field(..., description="JWT access token for Authorization header")
    token_type: str = Field(default="bearer", description="Token type for Authorization usage")


class DashboardFeature(BaseModel):
    """Feature descriptor for dashboard."""
    key: str = Field(..., description="Feature key")
    label: str = Field(..., description="Human-readable label")
    enabled: bool = Field(..., description="Whether the feature is enabled by package")
    limit: Optional[int] = Field(None, description="Optional quota limit")


class DashboardResponse(BaseModel):
    """Dashboard response summarizing user and available features."""
    user: UserPublic = Field(..., description="User profile")
    features: List[DashboardFeature] = Field(..., description="Features and entitlements for the user's package")


class TailoredContentResponse(BaseModel):
    """Response model for tailored content based on package tier."""
    summary: str = Field(..., description="Short description of content scope based on package")
    data_basic: List[str] = Field(..., description="Data available to all users")
    data_pro: Optional[List[str]] = Field(None, description="Additional data for pro and above")
    data_enterprise: Optional[List[str]] = Field(None, description="Additional data for enterprise only")
    analytics: Optional[dict] = Field(None, description="Enterprise analytics bundle")
