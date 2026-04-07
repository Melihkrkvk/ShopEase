import pytest

from tests.conftest import FakeProductRepository, FakeCache
from app.services.product_service import ProductService
from app.domain.product import Product


@pytest.fixture
def service(fake_product_repo, fake_cache):
    return ProductService(repo=fake_product_repo, cache=fake_cache)


@pytest.fixture
def seeded_service(fake_product_repo, fake_cache):
    """Service pre-loaded with two products."""
    svc = ProductService(repo=fake_product_repo, cache=fake_cache)
    svc.create(name="Widget", price=9.99, stock=10, category="tools")
    svc.create(name="Gadget", price=19.99, stock=5, category="electronics")
    return svc, fake_product_repo, fake_cache


# ---------------------------------------------------------------------------
# Basic CRUD
# ---------------------------------------------------------------------------


def test_create_returns_product_with_id(service):
    """create returns a Product with a database-assigned id."""
    product = service.create(name="Widget", price=9.99, stock=10, category="tools")
    assert product.id is not None
    assert product.name == "Widget"


def test_get_by_id_returns_correct_product(service):
    """get_by_id returns the product that was created."""
    created = service.create(name="Widget", price=9.99, stock=10, category="tools")
    fetched = service.get_by_id(created.id)
    assert fetched.name == "Widget"
    assert fetched.price == 9.99


def test_get_by_id_with_nonexistent_id_raises_value_error(service):
    """get_by_id raises ValueError when no product exists with the given id."""
    with pytest.raises(ValueError):
        service.get_by_id(999)


def test_get_all_returns_all_products(service):
    """get_all returns every created product."""
    service.create(name="A", price=1.0, stock=1, category="c")
    service.create(name="B", price=2.0, stock=2, category="c")
    assert len(service.get_all()) == 2


def test_update_changes_product_fields(service):
    """update modifies the specified fields and returns the updated product."""
    created = service.create(name="Widget", price=9.99, stock=10, category="tools")
    updated = service.update(created.id, price=4.99, stock=20)
    assert updated.price == 4.99
    assert updated.stock == 20


def test_delete_removes_product(service):
    """After delete, get_by_id raises ValueError for the deleted product."""
    created = service.create(name="Widget", price=9.99, stock=10, category="tools")
    service.delete(created.id)
    with pytest.raises(ValueError):
        service.get_by_id(created.id)


# ---------------------------------------------------------------------------
# Cache behaviour
# ---------------------------------------------------------------------------


def test_get_by_id_returns_cached_value_without_hitting_repo(fake_product_repo, fake_cache):
    """ProductService uses cache on second call — repository called only once."""
    service = ProductService(repo=fake_product_repo, cache=fake_cache)
    created = service.create(name="Widget", price=9.99, stock=10, category="tools")
    fake_product_repo.call_count = 0  # reset after create

    service.get_by_id(created.id)
    service.get_by_id(created.id)

    assert fake_product_repo.call_count == 1


def test_get_all_returns_cached_value_without_hitting_repo(fake_product_repo, fake_cache):
    """get_all uses cache on second call — repository called only once."""
    service = ProductService(repo=fake_product_repo, cache=fake_cache)
    service.create(name="Widget", price=9.99, stock=10, category="tools")
    fake_product_repo.call_count = 0

    service.get_all()
    service.get_all()

    assert fake_product_repo.call_count == 1


def test_create_invalidates_product_list_cache(fake_product_repo, fake_cache):
    """Creating a product clears the product list cache."""
    service = ProductService(repo=fake_product_repo, cache=fake_cache)
    service.get_all()  # populate cache
    service.create("Widget", 9.99, 10, "tools")
    assert fake_cache.get("products:all") is None


def test_update_invalidates_product_and_list_cache(fake_product_repo, fake_cache):
    """Updating a product invalidates both the individual and list cache entries."""
    service = ProductService(repo=fake_product_repo, cache=fake_cache)
    created = service.create("Widget", 9.99, 10, "tools")
    service.get_by_id(created.id)   # populate individual cache
    service.get_all()               # populate list cache
    service.update(created.id, price=1.0)
    assert fake_cache.get(f"product:{created.id}") is None
    assert fake_cache.get("products:all") is None


def test_delete_invalidates_product_and_list_cache(fake_product_repo, fake_cache):
    """Deleting a product invalidates both the individual and list cache entries."""
    service = ProductService(repo=fake_product_repo, cache=fake_cache)
    created = service.create("Widget", 9.99, 10, "tools")
    service.get_by_id(created.id)
    service.get_all()
    service.delete(created.id)
    assert fake_cache.get(f"product:{created.id}") is None
    assert fake_cache.get("products:all") is None
