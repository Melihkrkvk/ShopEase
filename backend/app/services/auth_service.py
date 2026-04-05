from app.core.security import create_access_token, decode_access_token, verify_password
from app.domain.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """
    Handles authentication: login and JWT token verification.

    Attributes:
        _repo (UserRepository): Repository for user lookups.
    """

    def __init__(self, repo: UserRepository) -> None:
        """
        Initialize AuthService.

        Args:
            repo (UserRepository): The user repository.
        """
        self._repo = repo

    def login(self, email: str, password: str) -> str:
        """
        Authenticate a user and return a signed JWT access token.

        Args:
            email (str): The user's email address.
            password (str): The plain-text password to verify.

        Returns:
            str: A signed JWT access token string.

        Raises:
            ValueError: If the email does not exist or the password is wrong.
        """
        user = self._repo.get_by_email(email)
        if user is None or not verify_password(password, user.password):
            raise ValueError("Invalid credentials")
        return create_access_token({"sub": str(user.id)})

    def get_current_user(self, token: str) -> User:
        """
        Decode a JWT token and return the corresponding user.

        Args:
            token (str): The JWT access token string.

        Returns:
            User: The authenticated user domain object.

        Raises:
            ValueError: If the token is invalid, expired, or the user no longer exists.
        """
        payload = decode_access_token(token)
        if payload is None:
            raise ValueError("Invalid token")
        user_id = int(payload["sub"])
        return self._repo.get_by_id(user_id)
