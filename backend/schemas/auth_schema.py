"""
schemas/auth_schema.py — Authentication Pydantic Schemas
=========================================================
Defines the request bodies and response shapes for all authentication
endpoints (register, login, current user, token).

Why separate from ORM models?
  - ORM models define DB columns.
  - Schemas define API contracts (what the client sends / receives).
  - Keeping them separate lets each evolve independently and prevents
    accidentally exposing sensitive DB fields (e.g. hashed_password).

Schemas
-------
UserRegisterRequest   → POST /auth/register  request body.
UserLoginRequest      → POST /auth/login     request body.
TokenResponse         → Response containing the JWT access token.
UserPublicResponse    → Safe public view of a user (no password).
CurrentUserResponse   → Response for GET /auth/me.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ─────────────────────────────────────────────────────────────────────────────
# Register
# ─────────────────────────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    """
    Request body for POST /auth/register.

    Attributes
    ----------
    username : str
        Desired username.  3–50 characters, alphanumeric + underscores.
    email : EmailStr
        Valid email address.  Pydantic validates the format.
    password : str
        Plain-text password.  8–128 characters.
        Will be hashed before storage — never stored in plain text.
    full_name : str, optional
        User's display name.  Optional.

    Example JSON
    ------------
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "full_name": "John Doe"
    }
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (3–50 alphanumeric characters).",
        examples=["john_doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address.",
        examples=["john@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8–128 characters).",
        examples=["SecurePass123!"],
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional display name.",
        examples=["John Doe"],
    )

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, value: str) -> str:
        """
        Ensure the username contains only letters, digits, and underscores.

        Raises
        ------
        ValueError
            If the username contains invalid characters.
        """
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
        if not all(c in allowed for c in value):
            raise ValueError("Username may only contain letters, digits, and underscores.")
        return value


# ─────────────────────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────────────────────

class UserLoginRequest(BaseModel):
    """
    Request body for POST /auth/login.

    Accepts either username or email as the identifier.

    Attributes
    ----------
    email : EmailStr
        Email address of the account to log in to.
    password : str
        Plain-text password to verify.

    Example JSON
    ------------
    {
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
    """

    email: EmailStr = Field(
        ...,
        description="Email address of the registered account.",
        examples=["john@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Account password.",
        examples=["SecurePass123!"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Token
# ─────────────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """
    Response body for POST /auth/login and POST /auth/register.

    Attributes
    ----------
    access_token : str
        The signed JWT access token the client should store and send
        in the ``Authorization: Bearer <token>`` header.
    token_type : str
        Always ``"bearer"`` per OAuth 2.0 conventions.
    expires_in : int
        Token lifetime in seconds.
    user : UserPublicResponse
        Basic public information about the authenticated user.

    Example JSON
    ------------
    {
        "access_token": "eyJhbGci...",
        "token_type": "bearer",
        "expires_in": 86400,
        "user": { "id": "...", "username": "john_doe", "email": "john@example.com" }
    }
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token validity in seconds.")
    user: "UserPublicResponse"

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Public User View
# ─────────────────────────────────────────────────────────────────────────────

class UserPublicResponse(BaseModel):
    """
    Safe, public-facing representation of a User.

    This schema deliberately excludes ``hashed_password`` and other
    sensitive fields that should never leave the server.

    Attributes
    ----------
    id : str
        UUID of the user.
    username : str
        Display username.
    email : str
        Email address.
    full_name : str or None
        Optional display name.
    is_active : bool
        Whether the account is active.
    created_at : str
        ISO-8601 creation timestamp.
    """

    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Current User (GET /auth/me)
# ─────────────────────────────────────────────────────────────────────────────

class CurrentUserResponse(BaseModel):
    """
    Response body for GET /auth/me (authenticated endpoint).

    Extended version of UserPublicResponse with additional stats.

    Attributes
    ----------
    id : str
        UUID of the user.
    username : str
        Display username.
    email : str
        Email address.
    full_name : str or None
        Optional display name.
    is_active : bool
        Account status.
    is_verified : bool
        Email verification status.
    created_at : str or None
        ISO-8601 account creation timestamp.
    total_projects : int
        Total number of design projects the user has created.
    """

    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: Optional[str] = None
    total_projects: int = 0

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Internal Token Payload (not an API schema)
# ─────────────────────────────────────────────────────────────────────────────

class TokenPayload(BaseModel):
    """
    Internal model representing the decoded JWT payload.

    Used by auth middleware to extract and validate the user ID
    from a Bearer token.

    Attributes
    ----------
    sub : str
        Subject — the user's UUID string.
    exp : int or None
        Expiry timestamp (UNIX epoch seconds).
    """

    sub: str
    exp: Optional[int] = None
