from pydantic import BaseModel


class ProductCreate(BaseModel):
    """Request schema for creating a new product."""

    name: str
    price: float
    stock: int
    category: str
    image_url: str | None = None
    description: str | None = None


class ProductUpdate(BaseModel):
    """Request schema for updating an existing product. All fields are optional."""

    name: str | None = None
    price: float | None = None
    stock: int | None = None
    category: str | None = None
    image_url: str | None = None
    description: str | None = None


class ProductResponse(BaseModel):
    """Response schema for a product resource."""

    id: int
    name: str
    price: float
    stock: int
    category: str
    image_url: str | None = None
    description: str | None = None
