from app.core.security import hash_password
from app.domain.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    """
    Manages user account operations.

    Attributes:
        _repo (UserRepository): Repository for user persistence.
    """

    def __init__(self, repo: UserRepository) -> None:
        """
        Initialize UserService.

        Args:
            repo (UserRepository): The user repository.
        """
        self._repo = repo

    def register(self, email: str, password: str, name: str) -> User:
        """
        Register a new user account.

        Args:
            email (str): The user's email address.
            password (str): The plain-text password to hash and store.
            name (str): The user's display name.

        Returns:
            User: The persisted user with its assigned id.

        Raises:
            ValueError: If the email address is already registered.
        """
        if self._repo.get_by_email(email) is not None:
            raise ValueError(f"{email} is already registered")
        hashed = hash_password(password)
        return self._repo.save(User(email=email, password=hashed, name=name))

    def get_by_id(self, id: int) -> User:
        """
        Retrieve a user by primary key.

        Args:
            id (int): The user's primary key.

        Returns:
            User: The corresponding user domain object.

        Raises:
            ValueError: If no user exists with the given id.
        """
        return self._repo.get_by_id(id)

    def get_all(self) -> list[User]:
        """Return all registered users."""
        return self._repo.get_all()
