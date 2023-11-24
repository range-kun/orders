from pydantic import BaseModel


class AuthModel(BaseModel):
    username: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class AuthenticatedUser(BaseModel):
    id: int
    is_active: bool
