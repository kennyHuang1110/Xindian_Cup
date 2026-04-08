"""Security helper functions for hashes and tokens."""

import hashlib


def hash_token(raw_value: str) -> str:
    """Return a SHA-256 digest for token storage."""
    return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()
