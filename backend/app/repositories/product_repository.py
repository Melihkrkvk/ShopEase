from app.dao.product_dao import ProductDAO
from app.domain.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository):
    """
    Repository for Product domain objects.

    Translates between raw dict rows (from ProductDAO) and Product domain objects.

    Attributes:
        _dao (ProductDAO): The DAO used for raw data access.
    """

    def __init__(self, dao: ProductDAO) -> None:
        """
        Initialize ProductRepository.

        Args:
            dao (ProductDAO): The data access object for the products table.
        """
        self._dao = dao

    def get_by_id(self, id: int) -> Product:
        """
        Retrieve a Product domain object by primary key.

        Args:
            id (int): The product's primary key.

        Returns:
            Product: The corresponding Product domain object.

        Raises:
            ValueError: If no product exists with the given id.
        """
        row = self._dao.find_by_id(id)
        if not row:
            raise ValueError(f"Product not found: {id}")
        return self._to_domain(row)

    def get_all(self) -> list[Product]:
        """Return all products as Product domain objects."""
        return [self._to_domain(row) for row in self._dao.find_all()]

    def search(self, query: str) -> list[Product]:
        """
        Search products by name.

        Args:
            query (str): The search term.

        Returns:
            list[Product]: Matching Product domain objects.
        """
        return [self._to_domain(row) for row in self._dao.search(query)]

    def get_by_category(self, category: str) -> list[Product]:
        """
        Retrieve all products in a given category.

        Args:
            category (str): The category label to filter by.

        Returns:
            list[Product]: Matching Product domain objects.
        """
        return [self._to_domain(row) for row in self._dao.find_by_category(category)]

    def save(self, product: Product) -> Product:
        """
        Persist a Product domain object and return it with its assigned id.

        Args:
            product (Product): The product to persist.

        Returns:
            Product: The persisted product with its database-assigned id.
        """
        data = {
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
            "category": product.category,
            "image_url": product.image_url,
            "description": product.description,
        }
        row = self._dao.insert(data)
        return self._to_domain(row)

    def update(self, id: int, **kwargs) -> Product:
        """
        Update an existing product by primary key.

        Args:
            id (int): The product's primary key.
            **kwargs: Fields to update (name, price, stock, category).

        Returns:
            Product: The updated Product domain object.

        Raises:
            ValueError: If no product exists with the given id.
        """
        row = self._dao.update(id, kwargs)
        if not row:
            raise ValueError(f"Product not found: {id}")
        return self._to_domain(row)

    def delete(self, id: int) -> None:
        """
        Delete a product by primary key.

        Args:
            id (int): The product's primary key.
        """
        self._dao.delete(id)

    def _to_domain(self, row: dict) -> Product:
        """
        Convert a raw DAO dict row into a Product domain object.

        Args:
            row (dict): A dict containing products table column values.

        Returns:
            Product: The corresponding Product domain object.
        """
        return Product(
            id=row["id"],
            name=row["name"],
            price=row["price"],
            stock=row["stock"],
            category=row["category"],
            image_url=row.get("image_url"),
            description=row.get("description"),
        )
