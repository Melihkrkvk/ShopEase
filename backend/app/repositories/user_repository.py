from app.dao.user_dao import UserDAO
from app.domain.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """
    Repository for User domain objects.

    Translates between raw dict rows (from UserDAO) and User domain objects.

    Attributes:
        _dao (UserDAO): The DAO used for raw data access.
    """

    def __init__(self, dao: UserDAO) -> None:
        """
        Initialize UserRepository.

        Args:
            dao (UserDAO): The data access object for the users table.
        """
        self._dao = dao

    def get_by_id(self, id: int) -> User:
        """
        Retrieve a User domain object by primary key.

        Args:
            id (int): The user's primary key.

        Returns:
            User: The corresponding User domain object.

        Raises:
            ValueError: If no user exists with the given id.
        """
        row = self._dao.find_by_id(id)
        if not row:
            raise ValueError(f"User not found: {id}")
        return self._to_domain(row)

    def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a User domain object by email address.

        Args:
            email (str): The email address to look up.

        Returns:
            User | None: The User if found, None otherwise.
        """
        row = self._dao.find_by_email(email)
        return self._to_domain(row) if row else None

    def save(self, user: User) -> User:
        """
        Persist a User domain object and return it with its assigned id.

        Args:
            user (User): The user to persist.

        Returns:
            User: The persisted user with its database-assigned id.
        """
        data = {"email": user.email, "password": user.password, "name": user.name}
        row = self._dao.insert(data)
        return self._to_domain(row)

    def delete(self, id: int) -> None:
        """
        Delete a user by primary key.

        Args:
            id (int): The user's primary key.
        """
        self._dao.delete(id)

    def get_all(self) -> list[User]:
        """Return all users as User domain objects."""
        return [self._to_domain(row) for row in self._dao.find_all()]

    def _to_domain(self, row: dict) -> User:
        """
        Convert a raw DAO dict row into a User domain object.

        Args:
            row (dict): A dict containing users table column values.

        Returns:
            User: The corresponding User domain object.
        """
        return User(
            id=row["id"],
            email=row["email"],
            password=row["password"],
            name=row["name"],
            is_admin=bool(row.get("is_admin", False)),
        )
