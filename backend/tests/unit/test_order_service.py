import pytest

from tests.conftest import FakeOrderRepository, FakeProductRepository, FakeCache
from app.services.order_service import OrderService
from app.services.cart_service import CartService
from app.services.product_service import ProductService
from app.services.payment_factory import PaymentFactory


@pytest.fixture
def product_service(fake_product_repo, fake_cache):
    return ProductService(repo=fake_product_repo, cache=fake_cache)


@pytest.fixture
def cart_service(fake_order_repo, product_service):
    return CartService(order_repo=fake_order_repo, product_service=product_service)


@pytest.fixture
def order_service(fake_order_repo, product_service, cart_service):
    return OrderService(
        order_repo=fake_order_repo,
        product_service=product_service,
        cart_service=cart_service,
        payment_factory=PaymentFactory(),
    )


@pytest.fixture
def product_and_cart(product_service, cart_service):
    """Pre-loaded cart: user 1 has 2 units of a product priced at 10.0."""
    product = product_service.create(name="Widget", price=10.0, stock=10, category="tools")
    cart_service.add_to_cart(user_id=1, product_id=product.id, quantity=2)
    return product


# ---------------------------------------------------------------------------
# place_order
# ---------------------------------------------------------------------------


def test_place_order_creates_order_with_correct_total(order_service, product_and_cart):
    """place_order calculates total from cart items and persists the order."""
    order = order_service.place_order(user_id=1, payment_method="credit_card")
    assert order.id is not None
    assert order.total == pytest.approx(20.0)
    assert order.user_id == 1
    assert order.payment_method == "credit_card"


def test_place_order_sets_status_to_pending(order_service, product_and_cart):
    """Newly placed order has status 'pending'."""
    order = order_service.place_order(user_id=1, payment_method="credit_card")
    assert order.status == "pending"


def test_place_order_clears_cart_after_success(order_service, cart_service, product_and_cart):
    """Cart is empty after a successful order is placed."""
    order_service.place_order(user_id=1, payment_method="credit_card")
    assert cart_service.get_cart(user_id=1) == []


def test_place_order_with_empty_cart_raises_value_error(order_service):
    """place_order raises ValueError when the user's cart is empty."""
    with pytest.raises(ValueError, match="empty"):
        order_service.place_order(user_id=99, payment_method="credit_card")


def test_place_order_with_invalid_payment_method_raises_value_error(order_service, product_and_cart):
    """place_order raises ValueError for an unknown payment method."""
    with pytest.raises(ValueError, match="Unknown payment method"):
        order_service.place_order(user_id=1, payment_method="carrier_pigeon")


# ---------------------------------------------------------------------------
# get_order / get_orders
# ---------------------------------------------------------------------------


def test_get_order_returns_correct_order(order_service, product_and_cart):
    """get_order returns the order that was placed."""
    placed = order_service.place_order(user_id=1, payment_method="credit_card")
    fetched = order_service.get_order(order_id=placed.id, user_id=1)
    assert fetched.id == placed.id


def test_get_order_for_wrong_user_raises_value_error(order_service, product_and_cart, fake_product_repo, fake_cache, fake_order_repo, cart_service):
    """get_order raises ValueError when the order belongs to a different user."""
    placed = order_service.place_order(user_id=1, payment_method="credit_card")
    with pytest.raises(ValueError, match="not found"):
        order_service.get_order(order_id=placed.id, user_id=2)


def test_get_orders_returns_all_user_orders(order_service, product_service, cart_service, product_and_cart):
    """get_orders returns every order placed by the user."""
    order_service.place_order(user_id=1, payment_method="credit_card")
    # add more items and place a second order
    product_service.create(name="Gadget", price=5.0, stock=5, category="electronics")
    cart_service.add_to_cart(user_id=1, product_id=2, quantity=1)
    order_service.place_order(user_id=1, payment_method="paypal")
    assert len(order_service.get_orders(user_id=1)) == 2


# ---------------------------------------------------------------------------
# Observer pattern
# ---------------------------------------------------------------------------


def test_place_order_notifies_all_observers(order_service, product_and_cart):
    """Every registered observer is called when an order is placed."""
    notified = []

    class FakeObserver:
        def on_order_placed(self, order):
            notified.append(order.id)

    obs1 = FakeObserver()
    obs2 = FakeObserver()
    order_service.register_observer(obs1)
    order_service.register_observer(obs2)

    order = order_service.place_order(user_id=1, payment_method="credit_card")
    assert notified.count(order.id) == 2


def test_place_order_without_observers_does_not_raise(order_service, product_and_cart):
    """place_order succeeds even when no observers are registered."""
    order = order_service.place_order(user_id=1, payment_method="credit_card")
    assert order.id is not None
