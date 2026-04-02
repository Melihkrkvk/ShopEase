from dataclasses import dataclass


@dataclass
class CartItem:
    """
    Domain object representing a single item in a shopping cart.

    Attributes:
        cart_id (int): The cart this item belongs to.
        product_id (int): The product being added.
        quantity (int): Number of units.
        id (int | None): Assigned by the database after persistence.
    """

    cart_id: int
    product_id: int
    quantity: int
    id: int | None = None
