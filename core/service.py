from typing import Generic

from core.repository import BaseAlchemyRepository
from core.schemas import PyModel, T


class BaseService(Generic[PyModel, T]):
    def __init__(self, repository: BaseAlchemyRepository, response_model: type[T]) -> None:
        self.repository = repository
        self.response_model = response_model

    async def add(self, model: PyModel) -> T:
        result = await self.repository.create(model.model_dump())
        return self.response_model(**result)

    async def retrieve(self, id_: int) -> T:
        instance = await self.repository.get_single(id=id_)
        return self.response_model(**instance)

    async def update_single(self, id_: int, model: PyModel) -> T:
        result = await self.repository.update(model.model_dump(), id=id_)
        return self.response_model(**result[0])

    async def delete(self, id_: int) -> None:
        await self.repository.delete(id=id_)


class KafkaInterface(Generic[PyModel, T]):
    payload_schema: type[PyModel]
    event_schema: type[T]
