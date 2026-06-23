"""Auth and user schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None
    tenant_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    full_name: str | None = None
    created_at: datetime


class TenantPublic(BaseModel):
    id: uuid.UUID
    name: str
    role: str


class RegisterResponse(BaseModel):
    user: UserPublic
    tenant: TenantPublic
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None = None
    active_tenant_id: uuid.UUID
    role: str
    mfa_enabled: bool


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    full_name: str | None = None
    email: EmailStr
    locale: str
    timezone: str
    default_autonomy_profile: str


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    locale: str | None = None
    timezone: str | None = None
    default_autonomy_profile: str | None = None


class MembershipItem(BaseModel):
    tenant_id: uuid.UUID
    tenant_name: str
    role: str
    joined_at: datetime
