from aiokafka import AIOKafkaProducer
from pydantic import ValidationError
from starlette import status

from core.errors import CategoryNotExistsError, NoRowsFoundError
from core.service import BaseService, KafkaInterface
from src.orders.repository import CategoryRepository, ProductRepository
from src.orders.schemas import (
    CategoryBase,
    CategoryOut,
    EventType,
    ProductCreate,
    ProductCreated,
    ProductEvent,
    ProductOut,
    ProductPayload,
)


class CategoryService(BaseService[CategoryBase, CategoryOut]):
    pass


class KafkaProductProducer(KafkaInterface[ProductPayload, ProductEvent]):
    payload_schema = ProductPayload
    event_schema = ProductEvent

    def __init__(self, producer: AIOKafkaProducer, kafka_topic: str):
        self.__producer = producer
        self.__kafka_topic = kafka_topic

    @staticmethod
    def encode_message(msg: str) -> bytes:
        if isinstance(msg, str):
            return bytes(msg, encoding="utf-8")

    async def send_message(self, topic: str, msg: str):
        if encoded_message := self.encode_message(msg):
            await self.__producer.send(topic, encoded_message)

    async def notify(self, method_name: EventType, data: dict):
        payload = self.payload_schema(**data)
        try:
            event_data = self.event_schema(event_type=method_name, payload=payload)  # for validation
        except ValidationError:
            return  # send data to log

        await self.send_message(self.__kafka_topic, event_data.model_dump_json())


class ProductOutService(BaseService[ProductCreate, ProductOut]):
    def __init__(
        self,
        repository: ProductRepository,
        response_model: type[ProductOut],
        category_repository: CategoryRepository,
        kafka_producer: KafkaProductProducer,
    ):
        self.__category_repository = category_repository
        self.__kafka_producer = kafka_producer
        super().__init__(repository, response_model)

    async def retrieve(self, id_: int) -> ProductOut:
        product = await self.repository.get_single(id=id_)
        try:
            category_row = await self.__category_repository.get_single(id=product["category_id"])
            category = CategoryOut(**category_row)  # type: CategoryOut | None
        except NoRowsFoundError:
            category = None
        return self.response_model(**self.create_product_output(product, category))

    async def delete(self, id_: int) -> None:
        await super().delete(id_)
        await self.__kafka_producer.notify(EventType.delete, {"id": id_})

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
        kafka_producer: KafkaProductProducer,
    ):
        self.category_repository = category_repository
        self.__kafka_producer = kafka_producer
        super().__init__(repository, response_model)

    async def add(self, product: ProductCreate) -> ProductCreated:
        category = await self.look_for_category(product)
        new_product = await super().add(product)

        payload = new_product.model_dump()
        payload["category"] = category

        await self.__kafka_producer.notify(EventType.add, payload)
        return new_product

    async def update_single(self, id_: int, product: ProductCreate) -> ProductCreated:
        category = await self.look_for_category(product)
        response = await super().update_single(id_=id_, model=product)

        payload = response.model_dump()
        payload["category"] = category

        await self.__kafka_producer.notify(EventType.update, payload)
        return response

    async def look_for_category(self, product: ProductCreate) -> dict:
        try:
            category = await self.category_repository.get_single(id=product.category_id)
        except NoRowsFoundError:
            raise CategoryNotExistsError(product.category_id, status_code=status.HTTP_400_BAD_REQUEST)
        return category
