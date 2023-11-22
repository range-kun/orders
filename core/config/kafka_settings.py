from kafka.conn import DEFAULT_KAFKA_PORT
from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    KAFKA_HOST: str = "localhost"
    KAFKA_PORT: int = DEFAULT_KAFKA_PORT
    PRODUCT_TOPIC: str = "default_topic"

    @property
    def kafka_url(self) -> str:
        return f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"
