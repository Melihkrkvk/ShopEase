from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_auth_service, get_user_service
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    body: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Register a new user account."""
    try:
        user = user_service.register(
            email=body.email, password=body.password, name=body.name
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return UserResponse(id=user.id, email=user.email, name=user.name, is_admin=user.is_admin)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate and return a JWT access token."""
    try:
        token = auth_service.login(email=body.email, password=body.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return TokenResponse(access_token=token)
