"""
utils/helpers.py — General-Purpose Helper Functions
=====================================================
Pure utility functions shared across the entire project.
These have no side-effects and no dependencies on FastAPI or
the database — they are safe to import anywhere.

Functions
---------
generate_uuid()         Generate a new UUID4 string.
utc_now()               Return the current UTC datetime.
format_datetime()       Format a datetime to an ISO-8601 string.
paginate()              Slice a list for pagination responses.
safe_get()              Access a nested dict key without KeyError.
mask_email()            Partially hide an email for safe logging.
build_storage_url()     Turn a relative storage path into a full URL.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional, TypeVar

T = TypeVar("T")


# ─────────────────────────────────────────────────────────────────────────────
# UUID
# ─────────────────────────────────────────────────────────────────────────────

def generate_uuid() -> str:
    """
    Generate a new UUID version 4 as a string.

    Returns
    -------
    str
        A hyphen-separated UUID4 string, e.g. ``"f47ac10b-58cc-4372-a567-0e02b2c3d479"``.

    Examples
    --------
    >>> uid = generate_uuid()
    >>> len(uid)
    36
    """
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────────────────────
# Time
# ─────────────────────────────────────────────────────────────────────────────

def utc_now() -> datetime:
    """
    Return the current UTC date and time as a timezone-aware datetime.

    Using timezone-aware datetimes prevents bugs when the server is
    deployed in a non-UTC timezone.

    Returns
    -------
    datetime
        Current time in UTC with tzinfo set.

    Examples
    --------
    >>> now = utc_now()
    >>> now.tzinfo
    datetime.timezone.utc
    """
    return datetime.now(tz=timezone.utc)


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Format a datetime object to an ISO-8601 string.

    Parameters
    ----------
    dt : datetime or None
        The datetime to format.

    Returns
    -------
    str or None
        ISO-8601 string (e.g. ``"2026-07-30T09:45:12+00:00"``) or
        ``None`` if input is ``None``.
    """
    if dt is None:
        return None
    return dt.isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Pagination
# ─────────────────────────────────────────────────────────────────────────────

def paginate(items: List[T], page: int = 1, page_size: int = 20) -> List[T]:
    """
    Slice a list to return only the items for the requested page.

    Parameters
    ----------
    items : list
        The full list of items to paginate.
    page : int
        1-based page number (default: 1).
    page_size : int
        Number of items per page (default: 20).

    Returns
    -------
    list
        A subset of ``items`` corresponding to the requested page.

    Examples
    --------
    >>> paginate(list(range(10)), page=2, page_size=3)
    [3, 4, 5]
    """
    page = max(1, page)
    page_size = max(1, min(page_size, 100))   # cap at 100 per page
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]


# ─────────────────────────────────────────────────────────────────────────────
# Safe Dict Access
# ─────────────────────────────────────────────────────────────────────────────

def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """
    Safely access a deeply nested key in a dictionary.

    Parameters
    ----------
    data : dict
        The dictionary to query.
    *keys : str
        Sequence of keys representing the path to the target value.
    default : any, optional
        Value returned if any key is missing (default: ``None``).

    Returns
    -------
    any
        The value at the nested path, or ``default`` if not found.

    Examples
    --------
    >>> d = {"a": {"b": {"c": 42}}}
    >>> safe_get(d, "a", "b", "c")
    42
    >>> safe_get(d, "a", "x", "c", default=0)
    0
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is default:
            return default
    return current


# ─────────────────────────────────────────────────────────────────────────────
# Privacy / Security Helpers
# ─────────────────────────────────────────────────────────────────────────────

def mask_email(email: str) -> str:
    """
    Partially obscure an email address for safe logging.

    Shows the first character and the domain; hides the rest of the
    local part with asterisks.

    Parameters
    ----------
    email : str
        The email address to mask.

    Returns
    -------
    str
        Masked email, e.g. ``"j****@example.com"``.

    Examples
    --------
    >>> mask_email("john.doe@example.com")
    'j*******@example.com'
    """
    if "@" not in email:
        return "****"
    local, domain = email.split("@", 1)
    masked_local = local[0] + "*" * max(1, len(local) - 1)
    return f"{masked_local}@{domain}"


# ─────────────────────────────────────────────────────────────────────────────
# Storage URL Builder
# ─────────────────────────────────────────────────────────────────────────────

def build_storage_url(relative_path: str, base_url: str = "http://localhost:8000") -> str:
    """
    Construct a fully qualified URL for a stored file.

    The frontend uses these URLs to load images and 3-D models.

    Parameters
    ----------
    relative_path : str
        Relative path returned from the API (e.g. ``"storage/uploads/abc.jpg"``).
    base_url : str
        API base URL (default: ``"http://localhost:8000"``).
        In production, pass the real domain.

    Returns
    -------
    str
        Full URL, e.g. ``"http://localhost:8000/storage/uploads/abc.jpg"``.

    Examples
    --------
    >>> build_storage_url("storage/uploads/abc.jpg")
    'http://localhost:8000/storage/uploads/abc.jpg'
    """
    relative_path = relative_path.lstrip("/")
    base_url = base_url.rstrip("/")
    return f"{base_url}/{relative_path}"
