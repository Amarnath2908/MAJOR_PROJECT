"""
middleware/auth.py — JWT Authentication Dependency
===================================================
Provides the FastAPI dependency get_current_user() that protected
routes use to identify the currently authenticated user.

How it works
------------
1. The client sends:  Authorization: Bearer <jwt_token>
2. get_current_user() extracts the token from the header.
3. It decodes the JWT using the SECRET_KEY and ALGORITHM from config.
4. It extracts the user ID from the token's 'sub' claim.
5. It queries the database to verify the user exists and is active.
6. It returns the User ORM object, available in the route handler.

Usage (in any route)
--------------------
    from middleware.auth import get_current_user
    from database.models import User

    @router.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        return {"user": current_user.username}
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from database.database import get_db
from database.models import User
from utils.logger import get_logger

logger = get_logger(__name__)

# HTTPBearer extracts the Bearer token from the Authorization header automatically.
# auto_error=True means it raises 403 if no Authorization header is present.
bearer_scheme = HTTPBearer(auto_error=True)


# ─────────────────────────────────────────────────────────────────────────────
# Token Decoder
# ─────────────────────────────────────────────────────────────────────────────

def decode_access_token(token: str) -> str:
    """
    Decode a JWT access token and extract the user ID.

    Parameters
    ----------
    token : str
        The raw JWT string (without the "Bearer " prefix).

    Returns
    -------
    str
        The ``sub`` claim from the token payload, which is the user's UUID.

    Raises
    ------
    HTTPException (401)
        If the token is expired, malformed, or missing the ``sub`` claim.

    Examples
    --------
    >>> user_id = decode_access_token("eyJhbGci...")
    >>> print(user_id)   # "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except ExpiredSignatureError:
        logger.warning("JWT token has expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as exc:
        logger.warning("JWT decode error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI Dependency
# ─────────────────────────────────────────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that authenticates the current request.

    Extracts the JWT from the Authorization header, decodes it,
    looks up the user in the database, and returns the User ORM object.

    Inject this into any route that requires authentication:

        @router.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return {"username": current_user.username}

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Automatically extracted from the ``Authorization: Bearer <token>``
        header by the HTTPBearer scheme.
    db : Session
        Database session injected by get_db().

    Returns
    -------
    User
        The authenticated User ORM object.

    Raises
    ------
    HTTPException (401)
        If the token is missing, expired, or invalid.
    HTTPException (401)
        If no user with the extracted ID exists in the database.
    HTTPException (403)
        If the user account is inactive / suspended.
    """
    token = credentials.credentials
    user_id = decode_access_token(token)

    user: User = db.query(User).filter(User.id == user_id).first()

    if user is None:
        logger.warning("Token references non-existent user: %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning("Inactive user attempted access: %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    logger.debug("Authenticated user: %s (%s)", user.username, user_id)
    return user


# ─────────────────────────────────────────────────────────────────────────────
# Optional Auth (for endpoints that work with or without a token)
# ─────────────────────────────────────────────────────────────────────────────

optional_bearer = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(optional_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Optional authentication dependency.

    Like get_current_user() but returns ``None`` instead of raising
    an error if no valid token is provided.

    Useful for endpoints that show public content but can personalise
    the response for authenticated users.

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials or None
        Bearer token if provided, else None.
    db : Session
        Database session.

    Returns
    -------
    User or None
        The authenticated user, or None if no token was provided.
    """
    if credentials is None:
        return None

    try:
        user_id = decode_access_token(credentials.credentials)
        user = db.query(User).filter(User.id == user_id).first()
        return user if (user and user.is_active) else None
    except HTTPException:
        return None
