from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.auth.dependencies import authenticate_user
from src.auth.schemas import AuthenticatedUser
from src.orders.dependencies import (
    get_category_service,
    get_product_service,
    get_product_service_update,
)
from src.orders.schemas import (
    CategoryBase,
    CategoryOut,
    ProductCreate,
    ProductCreated,
    ProductOut,
)
from src.orders.services import CategoryService, ProductCreateService, ProductOutService

CATEGORIES_PREFIX = "/categories"
PRODUCTS_PREFIX = "/products"

product_router = APIRouter(tags=["product"], prefix=PRODUCTS_PREFIX)
category_router = APIRouter(tags=["categories"], prefix=CATEGORIES_PREFIX)


@product_router.get("/{product_id}")
async def get_product(
    product_id: int,
    product_service: Annotated[ProductOutService, Depends(get_product_service)],
) -> ProductOut:
    return await product_service.retrieve(id_=product_id)


@product_router.put("/{product_id}")
async def change_product(
    product_id: int,
    product: ProductCreate,
    product_service: Annotated[ProductCreateService, Depends(get_product_service_update)],
    user: Annotated[AuthenticatedUser, Depends(authenticate_user)],
) -> ProductCreated:
    return await product_service.update_single(product_id, product)


@product_router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    product_service: Annotated[ProductOutService, Depends(get_product_service)],
    user: Annotated[AuthenticatedUser, Depends(authenticate_user)],
) -> Response:
    await product_service.delete(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@product_router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    product_service: Annotated[ProductCreateService, Depends(get_product_service_update)],
    user: Annotated[AuthenticatedUser, Depends(authenticate_user)],
) -> ProductCreated:
    return await product_service.add(product)


@category_router.post("", status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryBase,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    user: Annotated[AuthenticatedUser, Depends(authenticate_user)],
) -> CategoryOut:
    return await category_service.add(category)


@category_router.get("/{category_id}")
async def get_category(
    category_id: int,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryOut:
    return await category_service.retrieve(id_=category_id)


@category_router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    user: Annotated[AuthenticatedUser, Depends(authenticate_user)],
) -> Response:
    await category_service.delete(id_=category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
