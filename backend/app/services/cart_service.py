from threading import RLock

from app.domain.cart_item import CartItem
from app.repositories.order_repository import OrderRepository
from app.services.product_service import ProductService


class CartService:
    """
    Manages shopping cart operations with thread-safe stock enforcement.

    Uses RLock to prevent race conditions when multiple requests modify
    the same cart or compete for limited stock.

    Attributes:
        _order_repo (OrderRepository): Repository for cart persistence.
        _product_service (ProductService): Used to validate stock levels.
        _lock (RLock): Reentrant lock protecting add-to-cart operations.
    """

    def __init__(self, order_repo: OrderRepository, product_service: ProductService) -> None:
        """
        Initialize CartService.

        Args:
            order_repo (OrderRepository): The order/cart repository.
            product_service (ProductService): The product service for stock checks.
        """
        self._order_repo = order_repo
        self._product_service = product_service
        self._lock = RLock()

    def get_cart(self, user_id: int) -> list[CartItem]:
        """
        Return all items in the user's cart.

        Args:
            user_id (int): The user's primary key (used as cart_id).

        Returns:
            list[CartItem]: Cart items belonging to the user.
        """
        return self._order_repo.get_cart_items(cart_id=user_id)

    def add_to_cart(self, user_id: int, product_id: int, quantity: int) -> CartItem:
        """
        Add a product to the user's cart, enforcing stock limits.

        If the product is already in the cart, increments the quantity.
        Uses RLock to prevent overselling under concurrent requests.

        Args:
            user_id (int): The user's primary key.
            product_id (int): The product to add.
            quantity (int): Number of units to add.

        Returns:
            CartItem: The created or updated cart item.

        Raises:
            ValueError: If quantity is not positive.
            ValueError: If the requested quantity exceeds available stock.
        """
        if quantity <= 0:
            raise ValueError("quantity must be a positive integer")

        with self._lock:
            product = self._product_service.get_by_id(product_id)
            existing = self._order_repo.get_cart_item(cart_id=user_id, product_id=product_id)
            already_reserved = self._order_repo.get_total_reserved(product_id)
            new_quantity = (existing.quantity if existing else 0) + quantity
            total_after = already_reserved - (existing.quantity if existing else 0) + new_quantity

            if total_after > product.stock:
                raise ValueError(
                    f"Not enough stock: requested {total_after}, available {product.stock}"
                )

            if existing:
                assert existing.id is not None
                item = self._order_repo.update_cart_item(existing.id, new_quantity)
            else:
                item = self._order_repo.save_cart_item(
                    CartItem(cart_id=user_id, product_id=product_id, quantity=quantity)
                )

            return item

    def remove_from_cart(self, user_id: int, product_id: int) -> None:
        """
        Remove a product from the user's cart.

        Args:
            user_id (int): The user's primary key.
            product_id (int): The product to remove.

        Raises:
            ValueError: If the product is not in the user's cart.
        """
        item = self._order_repo.get_cart_item(cart_id=user_id, product_id=product_id)
        if item is None:
            raise ValueError(f"Product {product_id} is not in cart for user {user_id}")
        assert item.id is not None
        self._order_repo.delete_cart_item(item.id)

    def clear_cart(self, user_id: int) -> None:
        """
        Remove all items from the user's cart.

        Args:
            user_id (int): The user's primary key.
        """
        self._order_repo.clear_cart(cart_id=user_id)
