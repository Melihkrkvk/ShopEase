from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_cart_service, get_current_user, get_order_service, get_product_service
from app.domain.user import User
from app.schemas.order import (
    CartItemAdd,
    CartItemResponse,
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
)
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.payment_factory import PaymentFactory
from app.services.product_service import ProductService

router = APIRouter(tags=["orders"])

_payment_factory = PaymentFactory()


@router.get("/payment-methods", response_model=list[str])
def get_payment_methods() -> list[str]:
    """Return all available payment method keys."""
    return _payment_factory.get_available_payment_methods()


# ---------------------------------------------------------------------------
# Cart endpoints
# ---------------------------------------------------------------------------


@router.get("/cart", response_model=list[CartItemResponse])
def get_cart(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
    product_service: ProductService = Depends(get_product_service),
) -> list[CartItemResponse]:
    """Return all items in the current user's cart."""
    items = cart_service.get_cart(user_id=current_user.id)
    result = []
    for i in items:
        price = product_service.get_by_id(i.product_id).price
        result.append(CartItemResponse(
            id=i.id or 0,
            cart_id=i.cart_id,
            product_id=i.product_id,
            quantity=i.quantity,
            unit_price=price,
            total_price=round(price * i.quantity, 2),
        ))
    return result


@router.post("/cart/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    body: CartItemAdd,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
    product_service: ProductService = Depends(get_product_service),
) -> CartItemResponse:
    """Add a product to the current user's cart."""
    try:
        item = cart_service.add_to_cart(
            user_id=current_user.id,
            product_id=body.product_id,
            quantity=body.quantity,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    price = product_service.get_by_id(item.product_id).price
    return CartItemResponse(
        id=item.id or 0,
        cart_id=item.cart_id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=price,
        total_price=round(price * item.quantity, 2),
    )


@router.delete("/cart/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
) -> None:
    """Remove a product from the current user's cart."""
    try:
        cart_service.remove_from_cart(user_id=current_user.id, product_id=product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ---------------------------------------------------------------------------
# Order endpoints
# ---------------------------------------------------------------------------


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    body: OrderCreate,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Place an order using the current user's cart."""
    try:
        order = order_service.place_order(
            user_id=current_user.id, payment_method=body.payment_method
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        payment_method=order.payment_method,
        total=order.total,
        status=order.status,
    )


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    """Return all orders placed by the current user."""
    orders = order_service.get_orders(user_id=current_user.id)
    return [
        OrderResponse(
            id=o.id,
            user_id=o.user_id,
            payment_method=o.payment_method,
            total=o.total,
            status=o.status,
        )
        for o in orders
    ]


@router.get("/orders/{id}", response_model=OrderResponse)
def get_order(
    id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Return a single order by id, scoped to the current user."""
    try:
        order = order_service.get_order(order_id=id, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        payment_method=order.payment_method,
        total=order.total,
        status=order.status,
    )


@router.get("/orders/{id}/items", response_model=list[OrderItemResponse])
def get_order_items(
    id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> list[OrderItemResponse]:
    """Return all line items for an order, scoped to the current user."""
    try:
        items = order_service.get_order_items(order_id=id, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return [
        OrderItemResponse(
            id=i.id,
            order_id=i.order_id,
            product_id=i.product_id,
            quantity=i.quantity,
            unit_price=i.unit_price,
        )
        for i in items
    ]
