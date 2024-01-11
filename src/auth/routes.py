from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.auth.schemas import AuthModel, TokenPair
from src.auth.services import LoginService, RefreshService

AUTHENTICATION_PREFIX = "/authenticate"
auth_router = APIRouter(tags=["authenticate"], prefix=AUTHENTICATION_PREFIX)


@auth_router.post("/login", response_model=TokenPair)
async def login(
    request: Request, auth_model: AuthModel, login_service: Annotated[LoginService, Depends(LoginService)]
) -> JSONResponse:
    return await login_service(request, auth_model)


@auth_router.post("/refresh_token", response_model=TokenPair)
async def refresh(
    request: Request, refresh_service: Annotated[RefreshService, Depends(RefreshService)]
) -> JSONResponse:
    return await refresh_service(request)
