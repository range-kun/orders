from starlette.requests import Request

from src.auth.schemas import AuthenticatedUser
from src.auth.services import AuthUserService


async def authenticate_user(request: Request) -> AuthenticatedUser:
    auth_service = AuthUserService()
    return await auth_service(request)
