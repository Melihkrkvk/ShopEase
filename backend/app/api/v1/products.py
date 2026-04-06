from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_current_admin, get_current_user, get_product_service
from app.domain.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
def list_products(
    search: str | None = Query(None),
    category: str | None = Query(None),
    product_service: ProductService = Depends(get_product_service),
) -> list[ProductResponse]:
    """Return all products, optionally filtered by search term or category."""
    if search:
        products = product_service.search(search)
    elif category:
        products = product_service.get_by_category(category)
    else:
        products = product_service.get_all()
    return [
        ProductResponse(
            id=p.id, name=p.name, price=p.price, stock=p.stock, category=p.category,
            image_url=p.image_url, description=p.description,
        )
        for p in products
    ]


@router.get("/{id}", response_model=ProductResponse)
def get_product(
    id: int,
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Return a single product by id."""
    try:
        p = product_service.get_by_id(id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return ProductResponse(
        id=p.id, name=p.name, price=p.price, stock=p.stock, category=p.category,
        image_url=p.image_url, description=p.description,
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    body: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
    _admin: User = Depends(get_current_admin),
) -> ProductResponse:
    """Create a new product. Requires admin JWT."""
    p = product_service.create(
        name=body.name, price=body.price, stock=body.stock, category=body.category,
        image_url=body.image_url, description=body.description,
    )
    return ProductResponse(
        id=p.id, name=p.name, price=p.price, stock=p.stock, category=p.category,
        image_url=p.image_url, description=p.description,
    )


@router.put("/{id}", response_model=ProductResponse)
def update_product(
    id: int,
    body: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
    _admin: User = Depends(get_current_admin),
) -> ProductResponse:
    """Update an existing product. Requires admin JWT."""
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    try:
        p = product_service.update(id, **updates)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return ProductResponse(
        id=p.id, name=p.name, price=p.price, stock=p.stock, category=p.category,
        image_url=p.image_url, description=p.description,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    id: int,
    product_service: ProductService = Depends(get_product_service),
    _admin: User = Depends(get_current_admin),
) -> None:
    """Delete a product by id. Requires admin JWT."""
    product_service.delete(id)
