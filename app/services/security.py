"""Security helper functions for hashes and tokens."""

import hashlib
from secrets import token_urlsafe


def hash_token(raw_value: str) -> str:
    """Return a SHA-256 digest for token storage."""
    return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()


def generate_token(length: int = 32) -> str:
    """Generate a URL-safe random token."""
    return token_urlsafe(length)
