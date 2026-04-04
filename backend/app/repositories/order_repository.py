from app.dao.cart_item_dao import CartItemDAO
from app.dao.order_dao import OrderDAO
from app.dao.order_item_dao import OrderItemDAO
from app.domain.cart_item import CartItem
from app.domain.order import Order
from app.domain.order_item import OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository):
    """
    Repository for Order, OrderItem, and CartItem domain objects.

    Translates between raw dict rows (from DAOs) and domain objects.
    Also exposes cart operations used by CartService.

    Attributes:
        _order_dao (OrderDAO): DAO for the orders table.
        _order_item_dao (OrderItemDAO): DAO for the order_items table.
        _cart_dao (CartItemDAO): DAO for the cart_items table.
    """

    def __init__(
        self,
        order_dao: OrderDAO,
        cart_dao: CartItemDAO,
        order_item_dao: OrderItemDAO,
    ) -> None:
        """
        Initialize OrderRepository.

        Args:
            order_dao (OrderDAO): The data access object for the orders table.
            cart_dao (CartItemDAO): The data access object for the cart_items table.
            order_item_dao (OrderItemDAO): The data access object for the order_items table.
        """
        self._order_dao = order_dao
        self._cart_dao = cart_dao
        self._order_item_dao = order_item_dao

    def get_by_id(self, id: int) -> Order:
        """
        Retrieve an Order domain object by primary key.

        Args:
            id (int): The order's primary key.

        Returns:
            Order: The corresponding Order domain object.

        Raises:
            ValueError: If no order exists with the given id.
        """
        row = self._order_dao.find_by_id(id)
        if not row:
            raise ValueError(f"Order not found: {id}")
        return self._to_order_domain(row)

    def get_by_user_id(self, user_id: int) -> list[Order]:
        """
        Retrieve all orders placed by a user.

        Args:
            user_id (int): The user's primary key.

        Returns:
            list[Order]: Order domain objects.
        """
        return [self._to_order_domain(row) for row in self._order_dao.find_by_user_id(user_id)]

    def get_all(self) -> list[Order]:
        """Return all orders as Order domain objects."""
        return [self._to_order_domain(row) for row in self._order_dao.find_all()]

    def save(self, order: Order) -> Order:
        """
        Persist an Order domain object and return it with its assigned id.

        Args:
            order (Order): The order to persist.

        Returns:
            Order: The persisted order with its database-assigned id.
        """
        data = {
            "user_id": order.user_id,
            "payment_method": order.payment_method,
            "total": order.total,
            "status": order.status,
        }
        row = self._order_dao.insert(data)
        return self._to_order_domain(row)

    def update_status(self, id: int, status: str) -> Order:
        """
        Update the status of an order.

        Args:
            id (int): The order's primary key.
            status (str): The new status value.

        Returns:
            Order: The updated Order domain object.

        Raises:
            ValueError: If no order exists with the given id.
        """
        row = self._order_dao.update(id, {"status": status})
        if not row:
            raise ValueError(f"Order not found: {id}")
        return self._to_order_domain(row)

    def delete(self, id: int) -> None:
        """
        Delete an order by primary key.

        Args:
            id (int): The order's primary key.
        """
        self._order_dao.delete(id)

    # --- Cart operations ---

    def get_cart_items(self, cart_id: int) -> list[CartItem]:
        """
        Retrieve all items in a cart.

        Args:
            cart_id (int): The cart identifier (equal to user_id).

        Returns:
            list[CartItem]: CartItem domain objects.
        """
        return [self._to_cart_domain(row) for row in self._cart_dao.find_by_cart_id(cart_id)]

    def get_cart_item(self, cart_id: int, product_id: int) -> CartItem | None:
        """
        Retrieve a single cart item by cart and product.

        Args:
            cart_id (int): The cart identifier.
            product_id (int): The product's primary key.

        Returns:
            CartItem | None: The CartItem if found, None otherwise.
        """
        row = self._cart_dao.find_by_cart_and_product(cart_id, product_id)
        return self._to_cart_domain(row) if row else None

    def save_cart_item(self, item: CartItem) -> CartItem:
        """
        Persist a CartItem domain object and return it with its assigned id.

        Args:
            item (CartItem): The cart item to persist.

        Returns:
            CartItem: The persisted cart item with its database-assigned id.
        """
        data = {
            "cart_id": item.cart_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
        }
        row = self._cart_dao.insert(data)
        return self._to_cart_domain(row)

    def update_cart_item(self, id: int, quantity: int) -> CartItem:
        """
        Update the quantity of a cart item.

        Args:
            id (int): The cart item's primary key.
            quantity (int): The new quantity value.

        Returns:
            CartItem: The updated CartItem domain object.

        Raises:
            ValueError: If no cart item exists with the given id.
        """
        row = self._cart_dao.update(id, {"quantity": quantity})
        if not row:
            raise ValueError(f"CartItem not found: {id}")
        return self._to_cart_domain(row)

    def delete_cart_item(self, id: int) -> None:
        """
        Delete a single cart item by primary key.

        Args:
            id (int): The cart item's primary key.
        """
        self._cart_dao.delete(id)

    def clear_cart(self, cart_id: int) -> None:
        """
        Remove all items from a cart.

        Args:
            cart_id (int): The cart identifier to clear.
        """
        self._cart_dao.delete_by_cart_id(cart_id)

    def get_total_reserved(self, product_id: int) -> int:
        """
        Return total quantity of a product reserved across all carts.

        Args:
            product_id (int): The product's primary key.

        Returns:
            int: Sum of quantities for this product across all active carts.
        """
        rows = self._cart_dao.find_all()
        return sum(r["quantity"] for r in rows if r["product_id"] == product_id)

    def _to_order_domain(self, row: dict) -> Order:
        """
        Convert a raw DAO dict row into an Order domain object.

        Args:
            row (dict): A dict containing orders table column values.

        Returns:
            Order: The corresponding Order domain object.
        """
        return Order(
            id=row["id"],
            user_id=row["user_id"],
            payment_method=row["payment_method"],
            total=row["total"],
            status=row["status"],
        )

    # --- Order item operations ---

    def save_order_item(self, item: OrderItem) -> OrderItem:
        """
        Persist an OrderItem domain object and return it with its assigned id.

        Args:
            item (OrderItem): The order item to persist.

        Returns:
            OrderItem: The persisted order item with its database-assigned id.
        """
        data = {
            "order_id": item.order_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
        }
        row = self._order_item_dao.insert(data)
        return self._to_order_item_domain(row)

    def get_order_items(self, order_id: int) -> list[OrderItem]:
        """
        Retrieve all items belonging to an order.

        Args:
            order_id (int): The order's primary key.

        Returns:
            list[OrderItem]: OrderItem domain objects for the given order.
        """
        return [
            self._to_order_item_domain(row)
            for row in self._order_item_dao.find_by_order_id(order_id)
        ]

    def _to_order_item_domain(self, row: dict) -> OrderItem:
        """
        Convert a raw DAO dict row into an OrderItem domain object.

        Args:
            row (dict): A dict containing order_items table column values.

        Returns:
            OrderItem: The corresponding OrderItem domain object.
        """
        return OrderItem(
            id=row["id"],
            order_id=row["order_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            unit_price=row["unit_price"],
        )

    def _to_cart_domain(self, row: dict) -> CartItem:
        """
        Convert a raw DAO dict row into a CartItem domain object.

        Args:
            row (dict): A dict containing cart_items table column values.

        Returns:
            CartItem: The corresponding CartItem domain object.
        """
        return CartItem(
            id=row["id"],
            cart_id=row["cart_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
        )
