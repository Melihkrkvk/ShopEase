from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.cache.in_memory_cache import InMemoryCache
from app.cache.cache_service import CacheService
from app.core.database import get_db
from app.dao.cart_item_dao import CartItemDAO
from app.dao.order_dao import OrderDAO
from app.dao.order_item_dao import OrderItemDAO
from app.dao.product_dao import ProductDAO
from app.dao.user_dao import UserDAO
from app.domain.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.cart_service import CartService
from app.services.notification_service import EmailNotifier, InventoryUpdater
from app.services.order_service import OrderService
from app.services.payment_factory import PaymentFactory
from app.services.product_service import ProductService
from app.services.user_service import UserService

# Application-wide singletons
_cache: CacheService = InMemoryCache()
_payment_factory: PaymentFactory = PaymentFactory()

_order_service_instance: OrderService | None = None

bearer_scheme = HTTPBearer()


# ---------------------------------------------------------------------------
# DAO providers
# ---------------------------------------------------------------------------


def get_user_dao(db: Session = Depends(get_db)) -> UserDAO:
    """Provide a UserDAO instance for the current request."""
    return UserDAO(db)


def get_product_dao(db: Session = Depends(get_db)) -> ProductDAO:
    """Provide a ProductDAO instance for the current request."""
    return ProductDAO(db)


def get_order_dao(db: Session = Depends(get_db)) -> OrderDAO:
    """Provide an OrderDAO instance for the current request."""
    return OrderDAO(db)


def get_cart_item_dao(db: Session = Depends(get_db)) -> CartItemDAO:
    """Provide a CartItemDAO instance for the current request."""
    return CartItemDAO(db)


def get_order_item_dao(db: Session = Depends(get_db)) -> OrderItemDAO:
    """Provide an OrderItemDAO instance for the current request."""
    return OrderItemDAO(db)


# ---------------------------------------------------------------------------
# Repository providers
# ---------------------------------------------------------------------------


def get_user_repository(dao: UserDAO = Depends(get_user_dao)) -> UserRepository:
    """Provide a UserRepository wired to the current UserDAO."""
    return UserRepository(dao)


def get_product_repository(dao: ProductDAO = Depends(get_product_dao)) -> ProductRepository:
    """Provide a ProductRepository wired to the current ProductDAO."""
    return ProductRepository(dao)


def get_order_repository(
    order_dao: OrderDAO = Depends(get_order_dao),
    cart_dao: CartItemDAO = Depends(get_cart_item_dao),
    order_item_dao: OrderItemDAO = Depends(get_order_item_dao),
) -> OrderRepository:
    """Provide an OrderRepository wired to the current DAOs."""
    return OrderRepository(order_dao=order_dao, cart_dao=cart_dao, order_item_dao=order_item_dao)


# ---------------------------------------------------------------------------
# Cache provider
# ---------------------------------------------------------------------------


def get_cache() -> CacheService:
    """Provide the application-wide InMemoryCache singleton."""
    return _cache


# ---------------------------------------------------------------------------
# Service providers
# ---------------------------------------------------------------------------


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Provide a UserService with repository injected."""
    return UserService(repo=repo)


def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Provide an AuthService with repository injected."""
    return AuthService(repo=repo)


def get_product_service(
    repo: ProductRepository = Depends(get_product_repository),
    cache: CacheService = Depends(get_cache),
) -> ProductService:
    """Provide a ProductService with repository and cache injected."""
    return ProductService(repo=repo, cache=cache)


def get_cart_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    product_service: ProductService = Depends(get_product_service),
) -> CartService:
    """Provide a CartService with order repository and product service injected."""
    return CartService(order_repo=order_repo, product_service=product_service)


def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    product_service: ProductService = Depends(get_product_service),
    cart_service: CartService = Depends(get_cart_service),
) -> OrderService:
    """Provide an OrderService with all dependencies injected."""
    service = OrderService(
        order_repo=order_repo,
        product_service=product_service,
        cart_service=cart_service,
        payment_factory=_payment_factory,
    )
    service.register_observer(EmailNotifier())
    service.register_observer(InventoryUpdater(order_repo=order_repo, product_service=product_service))
    return service


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Extract and validate the JWT from the Authorization header.

    Returns:
        User: The authenticated user domain object.

    Raises:
        HTTPException 401: If the token is missing, invalid, or expired.
    """
    try:
        return auth_service.get_current_user(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require the current user to have admin privileges.

    Returns:
        User: The authenticated admin user.

    Raises:
        HTTPException 403: If the user does not have admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
