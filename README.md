# ShopEase

A full-stack e-commerce platform built as a university project. Features a FastAPI backend and a React frontend, developed with TDD principles and a strict layered architecture.

---

## Tech Stack

| Layer           | Technology                                     |
| --------------- | ---------------------------------------------- |
| Backend         | Python 3.12+, FastAPI, SQLAlchemy Core, SQLite |
| Auth            | bcrypt, python-jose (JWT)                      |
| Migrations      | Alembic                                        |
| Cache           | In-memory TTL cache (RLock)                    |
| Testing         | pytest, pytest-asyncio, httpx, pytest-cov      |
| Frontend        | React (Vite), Tailwind CSS, React Router       |
| Package manager | uv (backend), npm (frontend)                   |

---

## Architecture

| Document | Description |
| -------- | ----------- |
| [Class Diagram](docs/class_diagram.mdx) | Full class diagram — every class, its attributes, methods, and relationships |
| [High Level Design](docs/hld.mdx) | System layer diagram — how the five layers interact end-to-end |
| [Low Level Design](docs/lld.mdx) | Execution lifecycle — sequence diagrams for every major operation |

---

## Project Structure

```
shopease/
├── backend/
│   └── app/
│       ├── api/v1/        # FastAPI routers
│       ├── services/      # Business logic, cache
│       ├── repositories/  # Domain object mapping
│       ├── dao/           # Raw SQL queries
│       ├── domain/        # Pure Python dataclasses
│       ├── cache/         # CacheService ABC + InMemoryCache
│       └── core/          # Config, DB, security, DI wiring
└── frontend/
    └── src/
        ├── pages/         # LoginPage, RegisterPage, ProductsPage, CartPage, OrdersPage
        ├── components/    # Navbar, ProductCard, CartItem
        └── services/      # api.js, authService, productService, orderService
```

---

## Getting Started

### Prerequisites

| Tool    | Version | Install                                                     |
| ------- | ------- | ----------------------------------------------------------- |
| Python  | 3.12+   | [python.org](https://www.python.org/downloads/)             |
| uv      | latest  | `curl -LsSf https://astral.sh/uv/install.sh \| sh`          |
| Node.js | 18+     | [nodejs.org](https://nodejs.org/)                           |
| make    | —       | macOS: `xcode-select --install` · Linux: `apt install make` |

### 1 — Clone the repo

```bash
git clone https://github.com/<your-username>/shopease.git
cd shopease
```

### 2 — Configure environment (optional)

The backend works out of the box with SQLite and a default secret key. For a custom setup, create `backend/.env`:

```env
DATABASE_URL=sqlite:///./shopease.db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
CREDIT_CARD_MAX_AMOUNT=10000
PAYPAL_MAX_AMOUNT=5000
```

> **Production:** Set `DATABASE_URL` to a PostgreSQL connection string and use a strong `SECRET_KEY`.

### 3 — Backend setup

```bash
make backend-install   # install Python dependencies (uv sync)
make backend-dev       # start API server → http://localhost:8000
```

Optionally seed the database with sample products and test accounts:

```bash
make backend-seed
```

> Seed credentials: `admin@shopease.com / admin123` · `user@shopease.com / user123`

### 4 — Frontend setup

```bash
make frontend-install  # install Node dependencies (npm install)
make frontend-dev      # start dev server → http://localhost:5173
```

### Run both at once

```bash
make dev
```

### 5 — Verify

| URL                         | What               |
| --------------------------- | ------------------ |
| http://localhost:5173       | React frontend     |
| http://localhost:8000/docs  | FastAPI Swagger UI |
| http://localhost:8000/redoc | ReDoc API docs     |

---

## API Endpoints

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login

GET    /api/v1/users/me

GET    /api/v1/products          ?search=&category=
GET    /api/v1/products/{id}
POST   /api/v1/products          admin only
PUT    /api/v1/products/{id}     admin only
DELETE /api/v1/products/{id}     admin only

GET    /api/v1/cart
POST   /api/v1/cart/items
DELETE /api/v1/cart/items/{product_id}

POST   /api/v1/orders
GET    /api/v1/orders
GET    /api/v1/orders/{id}
GET    /api/v1/orders/{id}/items

GET    /api/v1/payment-methods
```

---

## Testing

```bash
make test              # all tests
make test-unit         # unit tests only (no DB)
make test-integration  # integration tests (in-memory SQLite)
make test-cov          # with coverage report
```

Target coverage: **80%+** (currently ~92%)

Unit tests use fake repositories and a fake cache — no real database. Integration tests use `TestClient` with `sqlite:///:memory:`.

---

## Payment Providers

Configured via environment variables:

```
CREDIT_CARD_MAX_AMOUNT=10000
PAYPAL_MAX_AMOUNT=5000
```

Adding a new payment method requires only a new `PaymentProvider` subclass registered in `PaymentFactory`.

---

## Database Tables

| Table         | Purpose                                               |
| ------------- | ----------------------------------------------------- |
| `users`       | Registered users with bcrypt passwords and admin flag |
| `products`    | Product catalogue                                     |
| `orders`      | Placed orders with payment method and status          |
| `order_items` | Line items with unit price snapshot at purchase time  |
| `cart_items`  | Temporary cart, cleared after order is placed         |
