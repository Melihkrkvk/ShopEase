from dataclasses import dataclass


@dataclass
class OrderItem:
    """
    Domain object representing a single line item within an order.

    Captures the product, quantity, and unit price at the time of purchase.
    The unit_price is stored separately so price changes do not affect
    historical order data.

    Attributes:
        order_id (int): The order this item belongs to.
        product_id (int): The product that was purchased.
        quantity (int): Number of units purchased.
        unit_price (float): Price per unit at the time of purchase.
        id (int | None): Assigned by the database after persistence.
    """

    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    id: int | None = None
