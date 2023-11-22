from starlette import status

from core.errors import CategoryNotExistsError, NoRowsFoundError
from core.service import BaseService
from src.orders.repository import CategoryRepository, ProductRepository
from src.orders.schemas import (
    CategoryBase,
    CategoryOut,
    ProductCreate,
    ProductCreated,
    ProductOut,
)


class CategoryService(BaseService[CategoryBase, CategoryOut]):
    pass


class ProductOutService(BaseService[ProductCreate, ProductOut]):
    def __init__(
        self, repository: ProductRepository, response_model: type[ProductOut], category_repository: CategoryRepository
    ):
        self.category_repository = category_repository
        super().__init__(repository, response_model)

    async def retrieve(self, id_: int) -> ProductOut:
        product = await self.repository.get_single(id=id_)
        try:
            category_row = await self.category_repository.get_single(id=product["category_id"])
            category = CategoryOut(**category_row)  # type: CategoryOut | None
        except NoRowsFoundError:
            category = None
        return self.response_model(**self.create_product_output(product, category))

    @staticmethod
    def create_product_output(product: dict, category: CategoryOut | None) -> dict:
        output = dict(product)
        output["category"] = category
        return output


class ProductCreateService(BaseService[ProductCreate, ProductCreated]):
    def __init__(
        self,
        repository: ProductRepository,
        response_model: type[ProductCreated],
        category_repository: CategoryRepository,
    ):
        self.category_repository = category_repository
        super().__init__(repository, response_model)

    async def add(self, product: ProductCreate) -> ProductCreated:
        try:
            await self.category_repository.get_single(id=product.category_id)
        except NoRowsFoundError:
            raise CategoryNotExistsError(product.category_id, status_code=status.HTTP_400_BAD_REQUEST)
        data = await self.repository.create(product.model_dump())
        return self.response_model(**data)
