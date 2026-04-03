from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class BaseDAO(ABC):
    """
    Abstract base class for all Data Access Objects.

    Defines the minimum CRUD interface every DAO must implement.
    All methods work with raw row data (dicts), not domain objects.

    Attributes:
        _db (Session): The active SQLAlchemy database session.
    """

    _db: Session

    def __init__(self, db: Session) -> None:
        """
        Initialize BaseDAO with a database session.

        Args:
            db (Session): The active database session to use for queries.
        """
        self._db = db

    @abstractmethod
    def find_by_id(self, id: int) -> dict | None:
        """
        Find a single row by primary key.

        Args:
            id (int): The primary key to look up.

        Returns:
            dict | None: Row as a dictionary, or None if not found.
        """
        ...

    @abstractmethod
    def insert(self, data: dict) -> dict:
        """
        Insert a new row and return the persisted row with its generated id.

        Args:
            data (dict): Column-value pairs to insert.

        Returns:
            dict: The inserted row including its generated primary key.
        """
        ...

    @abstractmethod
    def update(self, id: int, data: dict) -> dict | None:
        """
        Update a row by primary key.

        Args:
            id (int): The primary key of the row to update.
            data (dict): Column-value pairs to update.

        Returns:
            dict | None: The updated row, or None if not found.
        """
        ...

    @abstractmethod
    def delete(self, id: int) -> bool:
        """
        Delete a row by primary key.

        Args:
            id (int): The primary key of the row to delete.

        Returns:
            bool: True if a row was deleted, False if not found.
        """
        ...

    @abstractmethod
    def find_all(self) -> list[dict]:
        """Return all rows in the table as a list of dicts."""
        ...
