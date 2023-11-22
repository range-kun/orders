from starlette import status

from core.errors import CategoryNotExistsError, UpdateError
from core.repository import BaseAlchemyRepository
from src.orders.tables import categories, products


class CategoryRepository(BaseAlchemyRepository):
    table = categories


class ProductRepository(BaseAlchemyRepository):
    table = products

    async def update(self, data: dict, **filters) -> list[dict]:
        try:
            result = await super().update(data, **filters)
        except UpdateError:
            raise CategoryNotExistsError(data["category_id"], status_code=status.HTTP_400_BAD_REQUEST)
        return result
