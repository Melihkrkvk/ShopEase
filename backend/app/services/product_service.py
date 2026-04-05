from app.cache.cache_service import CacheService
from app.domain.product import Product
from app.repositories.product_repository import ProductRepository


class ProductService:
    """
    Manages product catalogue operations with integrated caching.

    Checks InMemoryCache before hitting the repository. Invalidates
    affected cache entries on every write operation.

    Attributes:
        _repo (ProductRepository): Repository for product persistence.
        _cache (CacheService): Cache for reducing repository calls.
    """

    def __init__(self, repo: ProductRepository, cache: CacheService) -> None:
        """
        Initialize ProductService.

        Args:
            repo (ProductRepository): The product repository.
            cache (CacheService): The cache implementation to use.
        """
        self._repo = repo
        self._cache = cache

    def get_by_id(self, id: int) -> Product:
        """
        Retrieve a product by id, using cache when available.

        Args:
            id (int): The product's primary key.

        Returns:
            Product: The product domain object.

        Raises:
            ValueError: If no product exists with the given id.
        """
        cached = self._cache.get(f"product:{id}")
        if cached is not None:
            return cached
        product = self._repo.get_by_id(id)
        self._cache.set(f"product:{id}", product, ttl=300)
        return product

    def get_all(self) -> list[Product]:
        """
        Return all products, using cache when available.

        Returns:
            list[Product]: All product domain objects.
        """
        cached = self._cache.get("products:all")
        if cached is not None:
            return cached
        products = self._repo.get_all()
        self._cache.set("products:all", products, ttl=300)
        return products

    def create(
        self,
        name: str,
        price: float,
        stock: int,
        category: str,
        image_url: str | None = None,
        description: str | None = None,
    ) -> Product:
        """
        Create a new product and invalidate the product list cache.

        Args:
            name (str): Product display name.
            price (float): Unit price in USD.
            stock (int): Initial inventory count.
            category (str): Product category label.
            image_url (str | None): Optional product image URL.
            description (str | None): Optional product description.

        Returns:
            Product: The persisted product with its assigned id.
        """
        product = self._repo.save(
            Product(name=name, price=price, stock=stock, category=category,
                    image_url=image_url, description=description)
        )
        self._cache.delete("products:all")
        return product

    def update(self, id: int, **kwargs) -> Product:
        """
        Update an existing product and invalidate related cache entries.

        Args:
            id (int): The product's primary key.
            **kwargs: Fields to update (name, price, stock, category).

        Returns:
            Product: The updated product domain object.
        """
        product = self._repo.update(id, **kwargs)
        self._cache.delete(f"product:{id}")
        self._cache.delete("products:all")
        return product

    def search(self, query: str) -> list[Product]:
        """
        Search products by name (case-insensitive partial match).

        Args:
            query (str): The search term.

        Returns:
            list[Product]: Matching product domain objects.
        """
        return self._repo.search(query)

    def get_by_category(self, category: str) -> list[Product]:
        """
        Return all products in the given category.

        Args:
            category (str): The category label to filter by.

        Returns:
            list[Product]: Matching product domain objects.
        """
        return self._repo.get_by_category(category)

    def delete(self, id: int) -> None:
        """
        Delete a product and invalidate related cache entries.

        Args:
            id (int): The product's primary key.
        """
        self._repo.delete(id)
        self._cache.delete(f"product:{id}")
        self._cache.delete("products:all")
