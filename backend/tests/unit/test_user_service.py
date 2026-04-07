import pytest

from tests.conftest import FakeUserRepository, FakeCache
from app.services.user_service import UserService
from app.services.auth_service import AuthService


@pytest.fixture
def user_service(fake_user_repo):
    return UserService(repo=fake_user_repo)


@pytest.fixture
def auth_service(fake_user_repo):
    return AuthService(repo=fake_user_repo)


# ---------------------------------------------------------------------------
# UserService tests
# ---------------------------------------------------------------------------


def test_register_creates_user_with_hashed_password(user_service):
    """Registered user is stored with a bcrypt hash, not the plain password."""
    user = user_service.register(email="a@b.com", password="secret", name="Alice")
    assert user.id is not None
    assert user.password != "secret"


def test_register_with_existing_email_raises_value_error(user_service):
    """Registering the same email twice raises ValueError."""
    user_service.register(email="a@b.com", password="secret", name="Alice")
    with pytest.raises(ValueError, match="already registered"):
        user_service.register(email="a@b.com", password="other", name="Bob")


def test_get_by_id_returns_correct_user(user_service):
    """get_by_id returns the user that was registered."""
    created = user_service.register(email="a@b.com", password="secret", name="Alice")
    fetched = user_service.get_by_id(created.id)
    assert fetched.email == "a@b.com"
    assert fetched.name == "Alice"


def test_get_by_id_with_nonexistent_id_raises_value_error(user_service):
    """get_by_id raises ValueError when no user exists with the given id."""
    with pytest.raises(ValueError):
        user_service.get_by_id(999)


def test_get_all_returns_all_registered_users(user_service):
    """get_all returns every registered user."""
    user_service.register(email="a@b.com", password="p", name="Alice")
    user_service.register(email="b@b.com", password="p", name="Bob")
    assert len(user_service.get_all()) == 2


# ---------------------------------------------------------------------------
# AuthService tests
# ---------------------------------------------------------------------------


def test_login_with_correct_credentials_returns_token(auth_service, fake_user_repo):
    """login returns a non-empty JWT string for valid credentials."""
    from app.services.user_service import UserService
    UserService(repo=fake_user_repo).register(
        email="a@b.com", password="secret", name="Alice"
    )
    token = auth_service.login(email="a@b.com", password="secret")
    assert isinstance(token, str)
    assert len(token) > 0


def test_login_with_wrong_password_raises_value_error(auth_service, fake_user_repo):
    """login raises ValueError when the password is incorrect."""
    from app.services.user_service import UserService
    UserService(repo=fake_user_repo).register(
        email="a@b.com", password="secret", name="Alice"
    )
    with pytest.raises(ValueError, match="Invalid credentials"):
        auth_service.login(email="a@b.com", password="wrong")


def test_login_with_nonexistent_email_raises_value_error(auth_service):
    """login raises ValueError when the email does not exist."""
    with pytest.raises(ValueError, match="Invalid credentials"):
        auth_service.login(email="nobody@b.com", password="x")


def test_get_current_user_returns_user_from_valid_token(auth_service, fake_user_repo):
    """get_current_user decodes a valid token and returns the correct user."""
    from app.services.user_service import UserService
    created = UserService(repo=fake_user_repo).register(
        email="a@b.com", password="secret", name="Alice"
    )
    token = auth_service.login(email="a@b.com", password="secret")
    user = auth_service.get_current_user(token)
    assert user.id == created.id


def test_get_current_user_with_invalid_token_raises_value_error(auth_service):
    """get_current_user raises ValueError for a tampered or invalid token."""
    with pytest.raises(ValueError, match="Invalid token"):
        auth_service.get_current_user("not.a.valid.token")
