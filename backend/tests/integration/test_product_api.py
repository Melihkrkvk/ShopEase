import pytest


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def admin_token(client, db_session):
    """Register an admin user and return their JWT token."""
    from sqlalchemy import text
    client.post("/api/v1/auth/register", json={"email": "admin@example.com", "password": "secret", "name": "Admin"})
    db_session.execute(text("UPDATE users SET is_admin = 1 WHERE email = 'admin@example.com'"))
    db_session.commit()
    resp = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "secret"})
    return resp.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    """Return Authorization headers for the admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


def _create_product(client, headers, **overrides):
    """Helper: create a product with defaults, return response JSON."""
    payload = {"name": "Widget", "price": 9.99, "stock": 10, "category": "tools", **overrides}
    return client.post("/api/v1/products", json=payload, headers=headers).json()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_list_products_returns_empty_list_initially(client):
    """GET /products returns an empty list when no products exist."""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product_requires_admin(client):
    """POST /products returns 403 for a non-admin user."""
    client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "secret", "name": "User"})
    resp = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "secret"})
    token = resp.json()["access_token"]

    response = client.post(
        "/api/v1/products",
        json={"name": "Widget", "price": 9.99, "stock": 10, "category": "tools"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_create_product_as_admin_returns_201(client, admin_headers):
    """POST /products as admin creates a product and returns 201."""
    response = client.post(
        "/api/v1/products",
        json={"name": "Widget", "price": 9.99, "stock": 10, "category": "tools"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99
    assert "id" in data


def test_create_product_with_image_url_and_description_returns_them(client, admin_headers):
    """POST /products with image_url and description returns them in the response."""
    response = client.post(
        "/api/v1/products",
        json={"name": "Widget", "price": 9.99, "stock": 10, "category": "tools",
              "image_url": "https://picsum.photos/seed/widget/600/600", "description": "A handy widget."},
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["image_url"] == "https://picsum.photos/seed/widget/600/600"
    assert data["description"] == "A handy widget."


def test_get_product_by_id_returns_product(client, admin_headers):
    """GET /products/{id} returns the product with all fields."""
    created = _create_product(
        client, admin_headers,
        image_url="https://picsum.photos/seed/widget/600/600",
        description="A handy widget.",
    )

    response = client.get(f"/api/v1/products/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Widget"
    assert data["image_url"] == "https://picsum.photos/seed/widget/600/600"
    assert data["description"] == "A handy widget."


def test_get_product_with_nonexistent_id_returns_404(client):
    """GET /products/999 returns 404 when the product does not exist."""
    response = client.get("/api/v1/products/999")
    assert response.status_code == 404


def test_list_products_includes_image_url_and_description(client, admin_headers):
    """GET /products returns image_url and description for each product."""
    _create_product(
        client, admin_headers,
        image_url="https://picsum.photos/seed/widget/600/600",
        description="A handy widget.",
    )

    data = client.get("/api/v1/products").json()
    assert data[0]["image_url"] == "https://picsum.photos/seed/widget/600/600"
    assert data[0]["description"] == "A handy widget."


def test_update_product_as_admin_returns_updated_product(client, admin_headers):
    """PUT /products/{id} as admin updates the product."""
    created = _create_product(client, admin_headers)

    response = client.put(
        f"/api/v1/products/{created['id']}",
        json={"price": 4.99},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["price"] == 4.99


def test_delete_product_as_admin_returns_204(client, admin_headers):
    """DELETE /products/{id} as admin removes the product."""
    created = _create_product(client, admin_headers)

    response = client.delete(f"/api/v1/products/{created['id']}", headers=admin_headers)
    assert response.status_code == 204
    assert client.get(f"/api/v1/products/{created['id']}").status_code == 404
