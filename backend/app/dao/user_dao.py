from sqlalchemy import text

from app.dao.base_dao import BaseDAO


class UserDAO(BaseDAO):
    """
    Data Access Object for the users table.

    Executes raw SQL via SQLAlchemy Core. Returns plain dicts — never
    domain objects. Business logic belongs in UserRepository or UserService.
    """

    def find_by_id(self, id: int) -> dict | None:
        """
        Find a user row by primary key.

        Args:
            id (int): The user's primary key.

        Returns:
            dict | None: User row as dict, or None if not found.
        """
        row = self._db.execute(
            text("SELECT * FROM users WHERE id = :id"), {"id": id}
        ).mappings().first()
        return dict(row) if row else None

    def find_by_email(self, email: str) -> dict | None:
        """
        Find a user row by email address.

        Args:
            email (str): The email address to search for.

        Returns:
            dict | None: User row as dict, or None if not found.
        """
        row = self._db.execute(
            text("SELECT * FROM users WHERE email = :email"), {"email": email}
        ).mappings().first()
        return dict(row) if row else None

    def insert(self, data: dict) -> dict:
        """
        Insert a new user row and return the persisted row with its id.

        Args:
            data (dict): Must contain 'email', 'password', and 'name' keys.

        Returns:
            dict: The inserted row including the generated primary key.
        """
        result = self._db.execute(
            text(
                "INSERT INTO users (email, password, name) "
                "VALUES (:email, :password, :name)"
            ),
            data,
        )
        last_id: int = result.lastrowid
        self._db.commit()
        row = self.find_by_id(last_id)
        assert row is not None
        return row

    def update(self, id: int, data: dict) -> dict | None:
        """
        Update a user row by primary key.

        Args:
            id (int): The user's primary key.
            data (dict): Column-value pairs to update.

        Returns:
            dict | None: The updated row, or None if not found.
        """
        self._db.execute(
            text("UPDATE users SET email = :email WHERE id = :id"),
            {**data, "id": id},
        )
        self._db.commit()
        return self.find_by_id(id)

    def delete(self, id: int) -> bool:
        """
        Delete a user row by primary key.

        Args:
            id (int): The user's primary key.

        Returns:
            bool: True if deleted, False if the row did not exist.
        """
        if self.find_by_id(id) is None:
            return False
        self._db.execute(text("DELETE FROM users WHERE id = :id"), {"id": id})
        self._db.commit()
        return True

    def find_all(self) -> list[dict]:
        """Return all user rows as a list of dicts."""
        rows = self._db.execute(text("SELECT * FROM users")).mappings().all()
        return [dict(row) for row in rows]
