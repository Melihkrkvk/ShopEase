from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Request schema for registering a new user."""

    email: EmailStr
    password: str
    name: str


class UserResponse(BaseModel):
    """Response schema for a user resource."""

    id: int
    email: str
    name: str
    is_admin: bool


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response schema returned after a successful login."""

    access_token: str
    token_type: str = "bearer"
