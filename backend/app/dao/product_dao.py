from sqlalchemy import text

from app.dao.base_dao import BaseDAO


class ProductDAO(BaseDAO):
    """
    Data Access Object for the products table.

    Executes raw SQL via SQLAlchemy Core. Returns plain dicts — never
    domain objects.
    """

    def find_by_id(self, id: int) -> dict | None:
        """
        Find a product row by primary key.

        Args:
            id (int): The product's primary key.

        Returns:
            dict | None: Product row as dict, or None if not found.
        """
        row = self._db.execute(
            text("SELECT * FROM products WHERE id = :id"), {"id": id}
        ).mappings().first()
        return dict(row) if row else None

    def find_all(self) -> list[dict]:
        """Return all product rows as a list of dicts."""
        rows = self._db.execute(text("SELECT * FROM products")).mappings().all()
        return [dict(row) for row in rows]

    def find_by_category(self, category: str) -> list[dict]:
        """
        Find all products in a given category.

        Args:
            category (str): The category label to filter by.

        Returns:
            list[dict]: Matching product rows as dicts.
        """
        rows = self._db.execute(
            text("SELECT * FROM products WHERE category = :category"),
            {"category": category},
        ).mappings().all()
        return [dict(row) for row in rows]

    def search(self, query: str) -> list[dict]:
        """
        Search products by name (case-insensitive partial match).

        Args:
            query (str): The search term.

        Returns:
            list[dict]: Matching product rows as dicts.
        """
        rows = self._db.execute(
            text("SELECT * FROM products WHERE LOWER(name) LIKE :q"),
            {"q": f"%{query.lower()}%"},
        ).mappings().all()
        return [dict(row) for row in rows]

    def insert(self, data: dict) -> dict:
        """
        Insert a new product row and return the persisted row with its id.

        Args:
            data (dict): Must contain 'name', 'price', 'stock', 'category' keys.

        Returns:
            dict: The inserted row including the generated primary key.
        """
        result = self._db.execute(
            text(
                "INSERT INTO products (name, price, stock, category, image_url, description) "
                "VALUES (:name, :price, :stock, :category, :image_url, :description)"
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
        Update a product row by primary key.

        Args:
            id (int): The product's primary key.
            data (dict): Column-value pairs to update (name, price, stock, category).

        Returns:
            dict | None: The updated row, or None if not found.
        """
        fields = ", ".join(f"{k} = :{k}" for k in data)
        self._db.execute(
            text(f"UPDATE products SET {fields} WHERE id = :id"),
            {**data, "id": id},
        )
        self._db.commit()
        return self.find_by_id(id)

    def delete(self, id: int) -> bool:
        """
        Delete a product row by primary key.

        Args:
            id (int): The product's primary key.

        Returns:
            bool: True if deleted, False if the row did not exist.
        """
        if self.find_by_id(id) is None:
            return False
        self._db.execute(text("DELETE FROM products WHERE id = :id"), {"id": id})
        self._db.commit()
        return True
