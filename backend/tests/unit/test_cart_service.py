import threading

import pytest

from tests.conftest import FakeOrderRepository, FakeProductRepository, FakeCache
from app.services.cart_service import CartService
from app.services.product_service import ProductService


@pytest.fixture
def product_service(fake_product_repo, fake_cache):
    return ProductService(repo=fake_product_repo, cache=fake_cache)


@pytest.fixture
def cart_service(fake_order_repo, product_service):
    return CartService(order_repo=fake_order_repo, product_service=product_service)


@pytest.fixture
def product(product_service):
    """A single product with 10 units of stock."""
    return product_service.create(name="Widget", price=9.99, stock=10, category="tools")


# ---------------------------------------------------------------------------
# Basic operations
# ---------------------------------------------------------------------------


def test_add_to_cart_creates_cart_item(cart_service, product):
    """add_to_cart creates a new CartItem for the user."""
    item = cart_service.add_to_cart(user_id=1, product_id=product.id, quantity=2)
    assert item.cart_id == 1
    assert item.product_id == product.id
    assert item.quantity == 2


def test_add_to_cart_existing_product_increments_quantity(cart_service, product):
    """Adding the same product twice increments the quantity."""
    cart_service.add_to_cart(user_id=1, product_id=product.id, quantity=2)
    item = cart_service.add_to_cart(user_id=1, product_id=product.id, quantity=3)
    assert item.quantity == 5


def test_add_to_cart_with_zero_quantity_raises_value_error(cart_service, product):
    """add_to_cart raises ValueError when quantity is zero."""
    with pytest.raises(ValueError, match="quantity"):
        cart_service.add_to_cart(user_id=1, product_id=product.id, quantity=0)


def test_add_to_cart_with_negative_quantity_raises_value_error(cart_service, product):
    """add_to_cart raises ValueError when quantity is negative."""
    with pytest.raises(ValueError, match="quantity"):
        cart_service.add_to_cart(user_id=1, product_id=product.id, quantity=-1)


def test_add_to_cart_exceeding_stock_raises_value_error(cart_service, product):
    """add_to_cart raises ValueError when quantity exceeds available stock."""
    with pytest.raises(ValueError, match="stock"):
        cart_service.add_to_cart(user_id=1, product_id=product.id, quantity=11)


def test_get_cart_returns_items_for_user(cart_service, product):
    """get_cart returns all items belonging to the user's cart."""
    cart_service.add_to_cart(user_id=1, product_id=product.id, quantity=2)
    items = cart_service.get_cart(user_id=1)
    assert len(items) == 1
    assert items[0].quantity == 2




def test_get_cart_returns_empty_list_for_new_user(cart_service):
    """get_cart returns an empty list when the user has no items."""
    assert cart_service.get_cart(user_id=99) == []


def test_remove_from_cart_deletes_item(cart_service, product):
    """remove_from_cart removes the product from the user's cart."""
    cart_service.add_to_cart(user_id=1, product_id=product.id, quantity=2)
    cart_service.remove_from_cart(user_id=1, product_id=product.id)
    assert cart_service.get_cart(user_id=1) == []


def test_remove_from_cart_with_nonexistent_product_raises_value_error(cart_service):
    """remove_from_cart raises ValueError when the product is not in the cart."""
    with pytest.raises(ValueError, match="not in cart"):
        cart_service.remove_from_cart(user_id=1, product_id=999)


def test_clear_cart_removes_all_items(cart_service, fake_product_repo, fake_cache):
    """clear_cart removes every item from the user's cart."""
    p2 = ProductService(repo=fake_product_repo, cache=fake_cache).create(
        name="Gadget", price=5.0, stock=5, category="electronics"
    )
    cart_service.add_to_cart(user_id=1, product_id=fake_product_repo.get_all()[0].id, quantity=1)
    cart_service.add_to_cart(user_id=1, product_id=p2.id, quantity=1)
    cart_service.clear_cart(user_id=1)
    assert cart_service.get_cart(user_id=1) == []


# ---------------------------------------------------------------------------
# Concurrency
# ---------------------------------------------------------------------------


def test_concurrent_add_to_cart_does_not_oversell(fake_order_repo, fake_product_repo, fake_cache):
    """Concurrent add_to_cart calls never exceed available stock."""
    product_service = ProductService(repo=fake_product_repo, cache=fake_cache)
    product = product_service.create(name="Limited", price=1.0, stock=5, category="test")
    cart_service = CartService(order_repo=fake_order_repo, product_service=product_service)

    errors = []

    def try_add(user_id):
        try:
            cart_service.add_to_cart(user_id=user_id, product_id=product.id, quantity=1)
        except ValueError:
            errors.append(user_id)

    threads = [threading.Thread(target=try_add, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    all_items = []
    for i in range(10):
        all_items.extend(fake_order_repo.get_cart_items(cart_id=i))

    total_quantity = sum(item.quantity for item in all_items)
    assert total_quantity <= 5
