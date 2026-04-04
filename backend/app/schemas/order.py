from pydantic import BaseModel


class CartItemAdd(BaseModel):
    """Request schema for adding a product to the cart."""

    product_id: int
    quantity: int


class CartItemResponse(BaseModel):
    """Response schema for a cart item resource."""

    id: int
    cart_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float


class OrderCreate(BaseModel):
    """Request schema for placing a new order."""

    payment_method: str


class OrderItemResponse(BaseModel):
    """Response schema for a single order line item."""

    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    """Response schema for an order resource."""

    id: int
    user_id: int
    payment_method: str
    total: float
    status: str
