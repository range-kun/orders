from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    AUTHENTICATION_SERVICE: str = "http://0.0.0.0:8000/api/v1"
    AUTHENTICATION_PATH: str = "/users/autorization"
    REFRESH_TOKEN_PATH: str = "/users/refresh_token"
    ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    @property
    def authentication_url(self) -> str:
        return f"{self.AUTHENTICATION_SERVICE}{self.AUTHENTICATION_PATH}"

    @property
    def refresh_token_url(self) -> str:
        return f"{self.AUTHENTICATION_SERVICE}{self.REFRESH_TOKEN_PATH}"
