from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(plain: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain (str): The plain-text password to hash.

    Returns:
        str: The bcrypt-hashed password string.
    """
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Args:
        plain (str): The plain-text password to check.
        hashed (str): The stored bcrypt hash.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    """
    Create a signed JWT access token.

    Args:
        data (dict): Claims to encode in the token (e.g. {'sub': user_id}).

    Returns:
        str: The encoded JWT string.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload["exp"] = expire
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    """
    Decode and verify a JWT access token.

    Args:
        token (str): The JWT string to decode.

    Returns:
        dict | None: The decoded payload, or None if the token is invalid or expired.
    """
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
