from sqlalchemy import text

from app.dao.base_dao import BaseDAO


class CartItemDAO(BaseDAO):
    """
    Data Access Object for the cart_items table.

    Executes raw SQL via SQLAlchemy Core. Returns plain dicts — never
    domain objects.
    """

    def find_by_id(self, id: int) -> dict | None:
        """
        Find a cart item row by primary key.

        Args:
            id (int): The cart item's primary key.

        Returns:
            dict | None: CartItem row as dict, or None if not found.
        """
        row = self._db.execute(
            text("SELECT * FROM cart_items WHERE id = :id"), {"id": id}
        ).mappings().first()
        return dict(row) if row else None

    def find_by_cart_id(self, cart_id: int) -> list[dict]:
        """
        Find all items in a given cart.

        Args:
            cart_id (int): The cart identifier (equal to user_id).

        Returns:
            list[dict]: CartItem rows as dicts.
        """
        rows = self._db.execute(
            text("SELECT * FROM cart_items WHERE cart_id = :cart_id"),
            {"cart_id": cart_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def find_by_cart_and_product(self, cart_id: int, product_id: int) -> dict | None:
        """
        Find a cart item by cart and product.

        Args:
            cart_id (int): The cart identifier.
            product_id (int): The product's primary key.

        Returns:
            dict | None: CartItem row as dict, or None if not found.
        """
        row = self._db.execute(
            text(
                "SELECT * FROM cart_items "
                "WHERE cart_id = :cart_id AND product_id = :product_id"
            ),
            {"cart_id": cart_id, "product_id": product_id},
        ).mappings().first()
        return dict(row) if row else None

    def find_all(self) -> list[dict]:
        """Return all cart item rows as a list of dicts."""
        rows = self._db.execute(text("SELECT * FROM cart_items")).mappings().all()
        return [dict(row) for row in rows]

    def insert(self, data: dict) -> dict:
        """
        Insert a new cart item row and return the persisted row with its id.

        Args:
            data (dict): Must contain 'cart_id', 'product_id', 'quantity'.

        Returns:
            dict: The inserted row including the generated primary key.
        """
        result = self._db.execute(
            text(
                "INSERT INTO cart_items (cart_id, product_id, quantity) "
                "VALUES (:cart_id, :product_id, :quantity)"
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
        Update a cart item row by primary key.

        Args:
            id (int): The cart item's primary key.
            data (dict): Column-value pairs to update.

        Returns:
            dict | None: The updated row, or None if not found.
        """
        fields = ", ".join(f"{k} = :{k}" for k in data)
        self._db.execute(
            text(f"UPDATE cart_items SET {fields} WHERE id = :id"),
            {**data, "id": id},
        )
        self._db.commit()
        return self.find_by_id(id)

    def delete(self, id: int) -> bool:
        """
        Delete a cart item row by primary key.

        Args:
            id (int): The cart item's primary key.

        Returns:
            bool: True if deleted, False if the row did not exist.
        """
        if self.find_by_id(id) is None:
            return False
        self._db.execute(text("DELETE FROM cart_items WHERE id = :id"), {"id": id})
        self._db.commit()
        return True

    def delete_by_cart_id(self, cart_id: int) -> None:
        """
        Delete all items in a cart.

        Args:
            cart_id (int): The cart identifier to clear.
        """
        self._db.execute(
            text("DELETE FROM cart_items WHERE cart_id = :cart_id"),
            {"cart_id": cart_id},
        )
        self._db.commit()
