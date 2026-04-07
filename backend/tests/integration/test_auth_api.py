import pytest


def test_register_returns_201_with_user_data(client):
    """POST /auth/register creates a user and returns 201 with user fields."""
    response = client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "password": "secret",
        "name": "Alice",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["name"] == "Alice"
    assert "id" in data
    assert "password" not in data


def test_register_with_duplicate_email_returns_400(client):
    """POST /auth/register with a duplicate email returns 400."""
    payload = {"email": "alice@example.com", "password": "secret", "name": "Alice"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


def test_login_with_valid_credentials_returns_token(client):
    """POST /auth/login returns a JWT access_token for valid credentials."""
    client.post("/api/v1/auth/register", json={
        "email": "alice@example.com", "password": "secret", "name": "Alice"
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "alice@example.com", "password": "secret"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401(client):
    """POST /auth/login with wrong password returns 401."""
    client.post("/api/v1/auth/register", json={
        "email": "alice@example.com", "password": "secret", "name": "Alice"
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "alice@example.com", "password": "wrong"
    })
    assert response.status_code == 401


def test_login_with_nonexistent_email_returns_401(client):
    """POST /auth/login with unknown email returns 401."""
    response = client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com", "password": "x"
    })
    assert response.status_code == 401


def test_get_me_with_valid_token_returns_user(client):
    """GET /users/me with valid JWT returns the authenticated user."""
    client.post("/api/v1/auth/register", json={
        "email": "alice@example.com", "password": "secret", "name": "Alice"
    })
    token_resp = client.post("/api/v1/auth/login", json={
        "email": "alice@example.com", "password": "secret"
    })
    token = token_resp.json()["access_token"]

    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_get_me_without_token_returns_401(client):
    """GET /users/me without Authorization header returns 401."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
