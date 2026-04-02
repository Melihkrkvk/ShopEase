from dataclasses import dataclass, field


@dataclass
class Order:
    """
    Domain object representing a placed order.

    Attributes:
        user_id (int): The id of the user who placed the order.
        payment_method (str): The payment method key used.
        total (float): The total amount charged.
        status (str): Current order status. Defaults to 'pending'.
        id (int | None): Assigned by the database after persistence.
    """

    user_id: int
    payment_method: str
    total: float
    status: str = "pending"
    id: int | None = None
