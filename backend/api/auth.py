"""
api/auth.py — Authentication API Routes
========================================
Defines all HTTP endpoints for user authentication.
Every endpoint delegates to auth_service — no business logic here.

Endpoints
---------
POST /auth/register    → Register a new user account.
POST /auth/login       → Authenticate and receive a JWT.
GET  /auth/me          → Get the current user's profile.
POST /auth/logout      → Logout placeholder (client drops token).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User
from middleware.auth import get_current_user, get_current_user_optional
from schemas.auth_schema import (
    CurrentUserResponse,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from services import auth_service
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Register
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Create a new DesignVerse AI account. "
        "On success, returns a JWT access token immediately so the user "
        "doesn't need to log in separately after registration."
    ),
)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Register a new user account.

    Parameters
    ----------
    request : UserRegisterRequest
        Registration payload: username, email, password, optional full_name.
    db : Session
        Injected database session.

    Returns
    -------
    TokenResponse
        JWT access token + public user data.

    Raises
    ------
    HTTPException 409
        If email or username is already registered.
    HTTPException 422
        If request body fails Pydantic validation.
    """
    logger.info("Register request for email: %s", request.email)
    return auth_service.register_user(db, request)


# ─────────────────────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    description=(
        "Authenticate with email and password. "
        "Returns a Bearer JWT token to include in subsequent requests."
    ),
)
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate a user and issue a JWT.

    Parameters
    ----------
    request : UserLoginRequest
        Login credentials: email and password.
    db : Session
        Injected database session.

    Returns
    -------
    TokenResponse
        JWT access token + public user data.

    Raises
    ------
    HTTPException 401
        If credentials are invalid.
    HTTPException 403
        If the account is inactive.
    """
    logger.info("Login request for email: %s", request.email)
    return auth_service.login_user(db, request)


# ─────────────────────────────────────────────────────────────────────────────
# Current User Profile
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description=(
        "Returns the profile of the currently authenticated user. "
        "Requires a valid Bearer token in the Authorization header."
    ),
)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentUserResponse:
    """
    Return the profile of the currently authenticated user.

    Parameters
    ----------
    current_user : User
        Injected from the JWT by get_current_user().
    db : Session
        Injected database session.

    Returns
    -------
    CurrentUserResponse
        Extended user profile including project count.

    Raises
    ------
    HTTPException 401
        If no valid Bearer token is provided.
    """
    return auth_service.get_current_user_profile(db, current_user)


# ─────────────────────────────────────────────────────────────────────────────
# Logout (Placeholder)
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout (client-side token discard)",
    description=(
        "Logout placeholder. JWTs are stateless — the client is responsible "
        "for discarding the token. Future implementation can add a token "
        "blocklist (Redis) for server-side invalidation."
    ),
)
def logout(
    current_user: User | None = Depends(get_current_user_optional),
) -> dict:
    """
    Logout placeholder endpoint.

    Since JWTs are stateless, true logout happens client-side by
    discarding the token. This endpoint:
    - Accepts optional token so clients with expired tokens can still logout cleanly.
    - Returns a success message.
    - Future: add token to a Redis blocklist for server-side invalidation.

    Returns
    -------
    dict
        Confirmation message.
    """
    username = current_user.username if current_user else "unauthenticated"
    logger.info("Logout: user=%s", username)
    return {
        "status": "success",
        "message": "Logged out successfully. Please discard your token.",
    }
