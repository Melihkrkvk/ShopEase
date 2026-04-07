import pytest
from sqlalchemy import text


def _register_login(client, email="user@example.com", password="secret", name="User"):
    """Register and return JWT token."""
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "name": name})
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _admin_token(client, db_session):
    """Register an admin and return their JWT token."""
    client.post("/api/v1/auth/register", json={
        "email": "admin@example.com", "password": "secret", "name": "Admin"
    })
    db_session.execute(text("UPDATE users SET is_admin = 1 WHERE email = 'admin@example.com'"))
    db_session.commit()
    resp = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "secret"})
    return resp.json()["access_token"]


def _create_product(client, admin_token, name="Widget", price=10.0, stock=10, category="tools"):
    """Create a product as admin and return its data."""
    return client.post(
        "/api/v1/products",
        json={"name": name, "price": price, "stock": stock, "category": category},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------


def test_get_cart_returns_empty_list_initially(client):
    """GET /cart returns an empty list for a new user."""
    token = _register_login(client)
    response = client.get("/api/v1/cart", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == []


def test_add_to_cart_returns_201_with_cart_item(client, db_session):
    """POST /cart/items adds a product and returns 201."""
    token = _register_login(client)
    admin = _admin_token(client, db_session)
    product = _create_product(client, admin)

    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == product["id"]
    assert data["quantity"] == 2


def test_add_to_cart_with_zero_quantity_returns_400(client, db_session):
    """POST /cart/items with quantity=0 returns 400."""
    token = _register_login(client)
    admin = _admin_token(client, db_session)
    product = _create_product(client, admin)

    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


def test_remove_from_cart_returns_204(client, db_session):
    """DELETE /cart/items/{product_id} removes the item and returns 204."""
    token = _register_login(client)
    admin = _admin_token(client, db_session)
    product = _create_product(client, admin)

    client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.delete(
        f"/api/v1/cart/items/{product['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------


def test_place_order_returns_201_with_order(client, db_session):
    """POST /orders places an order and returns 201."""
    token = _register_login(client)
    admin = _admin_token(client, db_session)
    product = _create_product(client, admin, price=10.0)

    client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        "/api/v1/orders",
        json={"payment_method": "credit_card"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["total"] == pytest.approx(20.0)
    assert data["status"] == "pending"


def test_place_order_with_empty_cart_returns_400(client):
    """POST /orders with an empty cart returns 400."""
    token = _register_login(client)
    response = client.post(
        "/api/v1/orders",
        json={"payment_method": "credit_card"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


def test_place_order_clears_the_cart(client, db_session):
    """After placing an order, GET /cart returns an empty list."""
    token = _register_login(client)
    admin = _admin_token(client, db_session)
    product = _create_product(client, admin)

    client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/v1/orders",
        json={"payment_method": "paypal"},
        headers={"Authorization": f"Bearer {token}"},
    )
    cart = client.get("/api/v1/cart", headers={"Authorization": f"Bearer {token}"})
    assert cart.json() == []


def test_list_orders_returns_placed_orders(client, db_session):
    """GET /orders returns all orders placed by the current user."""
    token = _register_login(client)
    admin = _admin_token(client, db_session)
    product = _create_product(client, admin)
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/cart/items", json={"product_id": product["id"], "quantity": 1}, headers=headers)
    client.post("/api/v1/orders", json={"payment_method": "credit_card"}, headers=headers)

    response = client.get("/api/v1/orders", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_order_by_id_returns_order(client, db_session):
    """GET /orders/{id} returns the order for the current user."""
    token = _register_login(client)
    admin = _admin_token(client, db_session)
    product = _create_product(client, admin)
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/cart/items", json={"product_id": product["id"], "quantity": 1}, headers=headers)
    order = client.post("/api/v1/orders", json={"payment_method": "credit_card"}, headers=headers).json()

    response = client.get(f"/api/v1/orders/{order['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == order["id"]


def test_get_order_items_returns_line_items(client, db_session):
    """GET /orders/{id}/items returns the products that were ordered."""
    token = _register_login(client)
    admin = _admin_token(client, db_session)
    product = _create_product(client, admin, price=10.0)
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/cart/items", json={"product_id": product["id"], "quantity": 3}, headers=headers)
    order = client.post("/api/v1/orders", json={"payment_method": "credit_card"}, headers=headers).json()

    response = client.get(f"/api/v1/orders/{order['id']}/items", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["product_id"] == product["id"]
    assert items[0]["quantity"] == 3
    assert items[0]["unit_price"] == pytest.approx(10.0)


def test_get_order_belonging_to_other_user_returns_404(client, db_session):
    """GET /orders/{id} returns 404 when the order belongs to another user."""
    token1 = _register_login(client, email="user1@example.com")
    token2 = _register_login(client, email="user2@example.com")
    admin = _admin_token(client, db_session)
    product = _create_product(client, admin)

    client.post("/api/v1/cart/items", json={"product_id": product["id"], "quantity": 1},
                headers={"Authorization": f"Bearer {token1}"})
    order = client.post("/api/v1/orders", json={"payment_method": "credit_card"},
                        headers={"Authorization": f"Bearer {token1}"}).json()

    response = client.get(f"/api/v1/orders/{order['id']}",
                          headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404
