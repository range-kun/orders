from fastapi import APIRouter

product_router = APIRouter(tags=["product"], prefix="/products")
category_router = APIRouter(tags=["categories"], prefix="/categories")


@product_router.get("/{product_id}")
async def get_product(product_id: int) -> None:
    pass


@product_router.put("/{product_id}")
async def update_product(product_id: int) -> None:
    pass


@product_router.delete("/{product_id}")
async def delete_product(product_id: int) -> None:
    pass


@product_router.post("")
async def create_product() -> None:
    pass


@category_router.post("")
async def create_category() -> None:
    pass


@category_router.get("/{category_id}")
async def get_category() -> None:
    pass


@category_router.delete("/{category_id}")
async def delete_category() -> None:
    pass
