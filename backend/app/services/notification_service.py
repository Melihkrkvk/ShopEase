from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.domain.order import Order

if TYPE_CHECKING:
    from app.repositories.order_repository import OrderRepository
    from app.services.product_service import ProductService


class OrderObserver(ABC):
    """
    Abstract base class for all order event observers.

    Implement this interface to receive notifications when an order is placed.
    """

    @abstractmethod
    def on_order_placed(self, order: Order) -> None:
        """
        Called after an order is successfully placed.

        Args:
            order (Order): The newly placed order domain object.
        """
        ...


class EmailNotifier(OrderObserver):
    """
    Observer that sends an order confirmation email.

    In production this would integrate with an email service.
    Currently logs to stdout for demonstration purposes.
    """

    def on_order_placed(self, order: Order) -> None:
        """
        Send a confirmation email for the placed order.

        Args:
            order (Order): The newly placed order domain object.
        """
        print(
            f"[EmailNotifier] Confirmation email sent for order #{order.id} "
            f"(user {order.user_id}, total ${order.total:.2f})"
        )


class InventoryUpdater(OrderObserver):
    """
    Observer that decrements product stock after an order is placed.

    Attributes:
        _order_repo (OrderRepository): Used to fetch order line items.
        _product_service (ProductService): Used to update product stock.
    """

    def __init__(self, order_repo: OrderRepository, product_service: ProductService) -> None:
        """
        Initialize InventoryUpdater.

        Args:
            order_repo (OrderRepository): Repository to retrieve order items.
            product_service (ProductService): Service to update product stock.
        """
        self._order_repo = order_repo
        self._product_service = product_service

    def on_order_placed(self, order: Order) -> None:
        """
        Decrement stock for every product in the order.

        Args:
            order (Order): The newly placed order domain object.
        """
        items = self._order_repo.get_order_items(order.id)
        for item in items:
            product = self._product_service.get_by_id(item.product_id)
            new_stock = max(0, product.stock - item.quantity)
            self._product_service.update(item.product_id, stock=new_stock)
        print(f"[InventoryUpdater] Stock decremented for order #{order.id}")
