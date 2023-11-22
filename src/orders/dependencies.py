from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine
from starlette.requests import Request

from src.orders.repository import CategoryRepository, ProductRepository
from src.orders.schemas import CategoryOut, ProductCreated, ProductOut
from src.orders.services import CategoryService, ProductCreateService, ProductOutService


def get_engine(request: Request):
    engine = create_async_engine(
        request.app.state.settings.ASYNC_DB_URL, future=True, echo=request.app.state.settings.DB_ECHO_LOG
    )
    yield engine


async def get_db(engine: Annotated[AsyncEngine, Depends(get_engine)]) -> AsyncGenerator[AsyncConnection, None]:
    async with engine.begin() as connection:
        yield connection


async def get_category_repository(connection: Annotated[AsyncConnection, Depends(get_db)]) -> CategoryRepository:
    return CategoryRepository(connection=connection)


async def get_category_service(
    category_repository: Annotated[CategoryRepository, Depends(get_category_repository)]
) -> CategoryService:
    return CategoryService(repository=category_repository, response_model=CategoryOut)


async def get_product_repository(connection: Annotated[AsyncConnection, Depends(get_db)]) -> ProductRepository:
    return ProductRepository(connection=connection)


async def get_product_service(
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)],
    category_repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> ProductOutService:
    return ProductOutService(
        repository=product_repository, response_model=ProductOut, category_repository=category_repository
    )


async def get_product_service_update(
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)],
    category_repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> ProductCreateService:
    return ProductCreateService(
        repository=product_repository,
        response_model=ProductCreated,
        category_repository=category_repository,
    )
