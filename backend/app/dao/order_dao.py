from sqlalchemy import text

from app.dao.base_dao import BaseDAO


class OrderDAO(BaseDAO):
    """
    Data Access Object for the orders table.

    Executes raw SQL via SQLAlchemy Core. Returns plain dicts — never
    domain objects.
    """

    def find_by_id(self, id: int) -> dict | None:
        """
        Find an order row by primary key.

        Args:
            id (int): The order's primary key.

        Returns:
            dict | None: Order row as dict, or None if not found.
        """
        row = self._db.execute(
            text("SELECT * FROM orders WHERE id = :id"), {"id": id}
        ).mappings().first()
        return dict(row) if row else None

    def find_by_user_id(self, user_id: int) -> list[dict]:
        """
        Find all orders belonging to a user.

        Args:
            user_id (int): The user's primary key.

        Returns:
            list[dict]: Order rows as dicts.
        """
        rows = self._db.execute(
            text("SELECT * FROM orders WHERE user_id = :user_id"),
            {"user_id": user_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def find_all(self) -> list[dict]:
        """Return all order rows as a list of dicts."""
        rows = self._db.execute(text("SELECT * FROM orders")).mappings().all()
        return [dict(row) for row in rows]

    def insert(self, data: dict) -> dict:
        """
        Insert a new order row and return the persisted row with its id.

        Args:
            data (dict): Must contain 'user_id', 'payment_method', 'total', 'status'.

        Returns:
            dict: The inserted row including the generated primary key.
        """
        result = self._db.execute(
            text(
                "INSERT INTO orders (user_id, payment_method, total, status) "
                "VALUES (:user_id, :payment_method, :total, :status)"
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
        Update an order row by primary key.

        Args:
            id (int): The order's primary key.
            data (dict): Column-value pairs to update.

        Returns:
            dict | None: The updated row, or None if not found.
        """
        fields = ", ".join(f"{k} = :{k}" for k in data)
        self._db.execute(
            text(f"UPDATE orders SET {fields} WHERE id = :id"),
            {**data, "id": id},
        )
        self._db.commit()
        return self.find_by_id(id)

    def delete(self, id: int) -> bool:
        """
        Delete an order row by primary key.

        Args:
            id (int): The order's primary key.

        Returns:
            bool: True if deleted, False if the row did not exist.
        """
        if self.find_by_id(id) is None:
            return False
        self._db.execute(text("DELETE FROM orders WHERE id = :id"), {"id": id})
        self._db.commit()
        return True
