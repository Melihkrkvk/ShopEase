import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.cache.cache_service import CacheService
from app.domain.cart_item import CartItem
from app.domain.order import Order
from app.domain.order_item import OrderItem
from app.domain.product import Product
from app.domain.user import User
from app.repositories.base import BaseRepository

TEST_DATABASE_URL = "sqlite:///:memory:"


# ---------------------------------------------------------------------------
# Fake repositories
# ---------------------------------------------------------------------------


class FakeUserRepository(BaseRepository):
    """In-memory UserRepository for unit tests. No database required."""

    def __init__(self) -> None:
        """Initialize the in-memory store and auto-increment counter."""
        self._store: dict[int, User] = {}
        self._next_id = 1

    def save(self, user: User) -> User:
        """Persist a user to the in-memory store and assign an id."""
        user.id = self._next_id
        self._store[self._next_id] = user
        self._next_id += 1
        return user

    def get_by_id(self, id: int) -> User:
        """Return user by id or raise ValueError if not found."""
        if id not in self._store:
            raise ValueError(f"User not found: {id}")
        return self._store[id]

    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email, or None."""
        return next((u for u in self._store.values() if u.email == email), None)

    def delete(self, id: int) -> None:
        """Remove a user from the in-memory store."""
        self._store.pop(id, None)

    def get_all(self) -> list[User]:
        """Return all users in the store."""
        return list(self._store.values())


class FakeProductRepository(BaseRepository):
    """In-memory ProductRepository for unit tests. No database required."""

    def __init__(self) -> None:
        """Initialize the in-memory store and auto-increment counter."""
        self._store: dict[int, Product] = {}
        self._next_id = 1
        self.call_count = 0

    def save(self, product: Product) -> Product:
        """Persist a product to the in-memory store and assign an id."""
        product.id = self._next_id
        self._store[self._next_id] = product
        self._next_id += 1
        return product

    def get_by_id(self, id: int) -> Product:
        """Return product by id or raise ValueError if not found."""
        self.call_count += 1
        if id not in self._store:
            raise ValueError(f"Product not found: {id}")
        return self._store[id]

    def get_all(self) -> list[Product]:
        """Return all products in the store."""
        self.call_count += 1
        return list(self._store.values())

    def update(self, id: int, **kwargs) -> Product:
        """Update a product in the store."""
        if id not in self._store:
            raise ValueError(f"Product not found: {id}")
        product = self._store[id]
        for k, v in kwargs.items():
            setattr(product, k, v)
        return product

    def delete(self, id: int) -> None:
        """Remove a product from the in-memory store."""
        self._store.pop(id, None)

    def search(self, query: str) -> list[Product]:
        """Return products whose name contains query (case-insensitive)."""
        return [p for p in self._store.values() if query.lower() in p.name.lower()]

    def get_by_category(self, category: str) -> list[Product]:
        """Return products in the given category."""
        return [p for p in self._store.values() if p.category == category]


class FakeOrderRepository:
    """In-memory OrderRepository for unit tests. No database required."""

    def __init__(self) -> None:
        """Initialize the in-memory stores and auto-increment counters."""
        self._orders: dict[int, Order] = {}
        self._cart_items: dict[int, CartItem] = {}
        self._order_items: dict[int, OrderItem] = {}
        self._next_order_id = 1
        self._next_cart_id = 1
        self._next_order_item_id = 1

    def get_by_id(self, id: int) -> Order:
        """Return order by id or raise ValueError if not found."""
        if id not in self._orders:
            raise ValueError(f"Order not found: {id}")
        return self._orders[id]

    def get_by_user_id(self, user_id: int) -> list[Order]:
        """Return all orders for a given user."""
        return [o for o in self._orders.values() if o.user_id == user_id]

    def get_all(self) -> list[Order]:
        """Return all orders."""
        return list(self._orders.values())

    def save(self, order: Order) -> Order:
        """Persist an order and assign an id."""
        order.id = self._next_order_id
        self._orders[self._next_order_id] = order
        self._next_order_id += 1
        return order

    def update_status(self, id: int, status: str) -> Order:
        """Update the status of an order."""
        if id not in self._orders:
            raise ValueError(f"Order not found: {id}")
        self._orders[id].status = status
        return self._orders[id]

    def delete(self, id: int) -> None:
        """Remove an order from the in-memory store."""
        self._orders.pop(id, None)

    def get_cart_items(self, cart_id: int) -> list[CartItem]:
        """Return all cart items for a given cart."""
        return [i for i in self._cart_items.values() if i.cart_id == cart_id]

    def get_cart_item(self, cart_id: int, product_id: int) -> CartItem | None:
        """Return a cart item by cart and product, or None."""
        return next(
            (i for i in self._cart_items.values()
             if i.cart_id == cart_id and i.product_id == product_id),
            None,
        )

    def save_cart_item(self, item: CartItem) -> CartItem:
        """Persist a cart item and assign an id."""
        item.id = self._next_cart_id
        self._cart_items[self._next_cart_id] = item
        self._next_cart_id += 1
        return item

    def update_cart_item(self, id: int, quantity: int) -> CartItem:
        """Update the quantity of a cart item."""
        if id not in self._cart_items:
            raise ValueError(f"CartItem not found: {id}")
        self._cart_items[id].quantity = quantity
        return self._cart_items[id]

    def delete_cart_item(self, id: int) -> None:
        """Remove a cart item from the in-memory store."""
        self._cart_items.pop(id, None)

    def clear_cart(self, cart_id: int) -> None:
        """Remove all items from a cart."""
        to_delete = [k for k, v in self._cart_items.items() if v.cart_id == cart_id]
        for k in to_delete:
            del self._cart_items[k]

    def get_total_reserved(self, product_id: int) -> int:
        """Return total quantity of a product reserved across all carts."""
        return sum(i.quantity for i in self._cart_items.values() if i.product_id == product_id)

    def save_order_item(self, item: OrderItem) -> OrderItem:
        """Persist an order item and assign an id."""
        item.id = self._next_order_item_id
        self._order_items[self._next_order_item_id] = item
        self._next_order_item_id += 1
        return item

    def get_order_items(self, order_id: int) -> list[OrderItem]:
        """Return all order items for a given order."""
        return [i for i in self._order_items.values() if i.order_id == order_id]


class FakeCache(CacheService):
    """In-memory CacheService for unit tests. TTL is accepted but not enforced."""

    def __init__(self) -> None:
        """Initialize an empty fake cache store."""
        self._store: dict[str, object] = {}

    def get(self, key: str) -> object | None:
        """Return stored value or None."""
        return self._store.get(key)

    def set(self, key: str, value: object, ttl: int = 300) -> None:
        """Store a value. TTL is ignored."""
        self._store[key] = value

    def delete(self, key: str) -> None:
        """Remove an entry. No-op if not present."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries."""
        self._store.clear()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_user_repo():
    """Provide an in-memory UserRepository for unit tests."""
    return FakeUserRepository()


@pytest.fixture
def fake_product_repo():
    """Provide an in-memory ProductRepository for unit tests."""
    return FakeProductRepository()


@pytest.fixture
def fake_order_repo():
    """Provide an in-memory OrderRepository for unit tests."""
    return FakeOrderRepository()


@pytest.fixture
def fake_cache():
    """Provide a FakeCache instance for unit tests."""
    return FakeCache()


@pytest.fixture(scope="function")
def db_session():
    """Provide a fresh in-memory SQLite session for each integration test."""
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from app.core.database import create_tables
    create_tables(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    """Provide a FastAPI test client wired to the test database."""
    from app.main import app
    from app.core.database import get_db
    from app.core.dependencies import _cache

    def override_get_db():
        yield db_session

    _cache.clear()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    _cache.clear()
