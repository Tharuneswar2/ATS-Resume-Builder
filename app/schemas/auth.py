"""
Pydantic schemas for authentication requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """Request body for user registration."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Ensure passwords meet minimum complexity requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Request body for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Sanitised user data returned to the client — never includes password."""
    id: str
    name: str
    email: str
    created_at: Optional[datetime] = None


class ChangePasswordRequest(BaseModel):
    """Request body for changing the current password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
