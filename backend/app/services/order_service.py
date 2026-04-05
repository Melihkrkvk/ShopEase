from threading import RLock

from app.domain.order import Order
from app.domain.order_item import OrderItem
from app.repositories.order_repository import OrderRepository
from app.services.cart_service import CartService
from app.services.notification_service import OrderObserver
from app.services.payment_factory import PaymentFactory
from app.services.product_service import ProductService


class OrderService:
    """
    Manages order placement and retrieval with Observer notifications.

    Coordinates cart, payment, and order persistence. Notifies all
    registered observers after a successful order.

    Attributes:
        _order_repo (OrderRepository): Repository for order persistence.
        _product_service (ProductService): Used to look up product prices.
        _cart_service (CartService): Used to read and clear the user's cart.
        _payment_factory (PaymentFactory): Factory for payment providers.
        _observers (list[OrderObserver]): Registered order event observers.
        _lock (RLock): Lock protecting order placement.
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        product_service: ProductService,
        cart_service: CartService,
        payment_factory: PaymentFactory,
    ) -> None:
        """
        Initialize OrderService.

        Args:
            order_repo (OrderRepository): The order repository.
            product_service (ProductService): The product service.
            cart_service (CartService): The cart service.
            payment_factory (PaymentFactory): The payment factory.
        """
        self._order_repo = order_repo
        self._product_service = product_service
        self._cart_service = cart_service
        self._payment_factory = payment_factory
        self._observers: list[OrderObserver] = []
        self._lock = RLock()

    def register_observer(self, observer: OrderObserver) -> None:
        """
        Register an observer to be notified when an order is placed.

        Args:
            observer (OrderObserver): The observer to add.
        """
        self._observers.append(observer)

    def place_order(self, user_id: int, payment_method: str) -> Order:
        """
        Place an order for the user's current cart.

        Validates the cart, processes payment, persists the order, clears
        the cart, and notifies all registered observers.

        Args:
            user_id (int): The user placing the order.
            payment_method (str): The payment method key to use.

        Returns:
            Order: The persisted order domain object.

        Raises:
            ValueError: If the cart is empty.
            ValueError: If the payment method is not recognized.
        """
        with self._lock:
            cart_items = self._cart_service.get_cart(user_id=user_id)
            if not cart_items:
                raise ValueError("Cannot place order: cart is empty")

            provider = self._payment_factory.create(payment_method)

            products = {
                item.product_id: self._product_service.get_by_id(item.product_id)
                for item in cart_items
            }
            total = sum(
                products[item.product_id].price * item.quantity
                for item in cart_items
            )

            result = provider.process(amount=total)
            if not result:
                raise ValueError(f"Payment failed: {result.message}")

            order = self._order_repo.save(
                Order(
                    user_id=user_id,
                    payment_method=payment_method,
                    total=total,
                    status="pending",
                )
            )
            assert order.id is not None

            for item in cart_items:
                self._order_repo.save_order_item(
                    OrderItem(
                        order_id=order.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        unit_price=products[item.product_id].price,
                    )
                )

            self._cart_service.clear_cart(user_id=user_id)

            for observer in self._observers:
                observer.on_order_placed(order)

            return order

    def get_order(self, order_id: int, user_id: int) -> Order:
        """
        Retrieve an order by id, scoped to the requesting user.

        Args:
            order_id (int): The order's primary key.
            user_id (int): The user requesting the order.

        Returns:
            Order: The matching order domain object.

        Raises:
            ValueError: If the order does not exist or belongs to a different user.
        """
        order = self._order_repo.get_by_id(order_id)
        if order.user_id != user_id:
            raise ValueError(f"Order {order_id} not found for user {user_id}")
        return order

    def get_order_items(self, order_id: int, user_id: int) -> list[OrderItem]:
        """
        Return all items belonging to an order, scoped to the requesting user.

        Args:
            order_id (int): The order's primary key.
            user_id (int): The user requesting the items.

        Returns:
            list[OrderItem]: Line items for the given order.

        Raises:
            ValueError: If the order does not exist or belongs to a different user.
        """
        self.get_order(order_id=order_id, user_id=user_id)
        return self._order_repo.get_order_items(order_id)

    def get_orders(self, user_id: int) -> list[Order]:
        """
        Return all orders placed by the user.

        Args:
            user_id (int): The user's primary key.

        Returns:
            list[Order]: All orders for the given user.
        """
        return self._order_repo.get_by_user_id(user_id=user_id)
