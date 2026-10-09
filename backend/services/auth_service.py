"""
services/auth_service.py — Authentication Business Logic
=========================================================
Contains ALL business logic for user authentication.
API routes (api/auth.py) call these functions — they never
touch the database or hashing directly.

Functions
---------
hash_password()        Hash a plain-text password using bcrypt.
verify_password()      Compare a plain password against a bcrypt hash.
create_access_token()  Encode a signed JWT access token.
register_user()        Validate uniqueness, hash password, create user row.
login_user()           Verify credentials, return a JWT token response.
get_user_by_id()       Fetch a user by their UUID (used by auth middleware).
get_user_by_email()    Fetch a user by email address.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config import settings
from database.models import User
from schemas.auth_schema import (
    CurrentUserResponse,
    TokenResponse,
    UserPublicResponse,
    UserRegisterRequest,
    UserLoginRequest,
)
from utils.helpers import format_datetime, generate_uuid
from utils.logger import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Password Hashing Context
# ─────────────────────────────────────────────────────────────────────────────

# bcrypt is the recommended algorithm for password hashing.
# 'deprecated="auto"' means older hashes are auto-upgraded on next login.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─────────────────────────────────────────────────────────────────────────────
# Password Utilities
# ─────────────────────────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    The resulting hash is safe to store in the database.
    The salt is embedded in the hash itself, so no separate salt
    column is needed.

    Parameters
    ----------
    plain_password : str
        The raw password string entered by the user.

    Returns
    -------
    str
        A bcrypt hash string, e.g. ``"$2b$12$..."`` (60 chars).

    Examples
    --------
    >>> h = hash_password("MySecret123!")
    >>> h.startswith("$2b$")
    True
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches a stored bcrypt hash.

    Parameters
    ----------
    plain_password : str
        The raw password provided at login.
    hashed_password : str
        The bcrypt hash retrieved from the database.

    Returns
    -------
    bool
        ``True`` if the password matches; ``False`` otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ─────────────────────────────────────────────────────────────────────────────
# JWT Token
# ─────────────────────────────────────────────────────────────────────────────

def create_access_token(user_id: str) -> tuple[str, int]:
    """
    Create a signed JWT access token for a user.

    The token payload contains:
      - ``sub``: the user's UUID string (subject).
      - ``exp``: expiry timestamp in UNIX epoch seconds.
      - ``iat``: issued-at timestamp.

    Parameters
    ----------
    user_id : str
        The UUID of the user to encode in the token.

    Returns
    -------
    tuple[str, int]
        A tuple of (token_string, expires_in_seconds).

    Examples
    --------
    >>> token, expires = create_access_token("f47ac10b-...")
    >>> print(token[:10])
    'eyJhbGciOi'
    """
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return token, expires_in_seconds


# ─────────────────────────────────────────────────────────────────────────────
# Database Lookups
# ─────────────────────────────────────────────────────────────────────────────

def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Fetch a User record by its UUID primary key.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    user_id : str
        UUID string of the user to look up.

    Returns
    -------
    User or None
        The User ORM object, or ``None`` if no match is found.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Fetch a User record by email address (case-insensitive).

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    email : str
        Email address to search for.

    Returns
    -------
    User or None
        The User ORM object, or ``None`` if no match is found.
    """
    return db.query(User).filter(User.email == email.lower().strip()).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Fetch a User record by username.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    username : str
        Username to search for.

    Returns
    -------
    User or None
        The User ORM object, or ``None`` if no match is found.
    """
    return db.query(User).filter(User.username == username).first()


# ─────────────────────────────────────────────────────────────────────────────
# Register
# ─────────────────────────────────────────────────────────────────────────────

def register_user(db: Session, request: UserRegisterRequest) -> TokenResponse:
    """
    Register a new user account.

    Steps
    -----
    1. Normalise email to lowercase.
    2. Check that the email is not already registered.
    3. Check that the username is not already taken.
    4. Hash the password.
    5. Create and persist a new User row.
    6. Issue a JWT token and return a TokenResponse.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    request : UserRegisterRequest
        Validated registration payload from the client.

    Returns
    -------
    TokenResponse
        JWT access token and public user data.

    Raises
    ------
    HTTPException (409 Conflict)
        If the email or username is already taken.
    """
    email = request.email.lower().strip()

    # ── Uniqueness checks ─────────────────────────────────────────────────────
    if get_user_by_email(db, email):
        logger.warning("Registration attempt with existing email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    if get_user_by_username(db, request.username):
        logger.warning("Registration attempt with taken username: %s", request.username)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken. Please choose another.",
        )

    # ── Create user ───────────────────────────────────────────────────────────
    user = User(
        id=generate_uuid(),
        username=request.username,
        email=email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("New user registered: %s (%s)", user.username, user.id)

    # ── Issue token ───────────────────────────────────────────────────────────
    token, expires_in = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserPublicResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=format_datetime(user.created_at),
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────────────────────

def login_user(db: Session, request: UserLoginRequest) -> TokenResponse:
    """
    Authenticate a user and issue a JWT token.

    Steps
    -----
    1. Look up the user by email.
    2. Verify the provided password against the stored bcrypt hash.
    3. Check the account is active.
    4. Issue a JWT and return a TokenResponse.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    request : UserLoginRequest
        Login credentials from the client.

    Returns
    -------
    TokenResponse
        JWT access token and public user data.

    Raises
    ------
    HTTPException (401 Unauthorized)
        If the email is not found or the password is incorrect.
    HTTPException (403 Forbidden)
        If the account is inactive.
    """
    email = request.email.lower().strip()
    user = get_user_by_email(db, email)

    # Deliberately use the same error message for "not found" and
    # "wrong password" to prevent user enumeration attacks.
    if user is None or not verify_password(request.password, user.hashed_password):
        logger.warning("Failed login attempt for email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email address or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact support.",
        )

    logger.info("User logged in: %s (%s)", user.username, user.id)

    token, expires_in = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserPublicResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=format_datetime(user.created_at),
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Current User Profile
# ─────────────────────────────────────────────────────────────────────────────

def get_current_user_profile(db: Session, user: User) -> CurrentUserResponse:
    """
    Build the full profile response for the currently authenticated user.

    Includes aggregated stats like total project count.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    user : User
        The currently authenticated User ORM object.

    Returns
    -------
    CurrentUserResponse
        Extended user profile with stats.
    """
    from database.models import Project
    total_projects = db.query(Project).filter(Project.user_id == user.id).count()

    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=format_datetime(user.created_at),
        total_projects=total_projects,
    )
