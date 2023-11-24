import ast

from jose import jwt
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.errors import NotAuthenticated, NotValidToken
from core.service import AuthInterface
from src.auth.mixins import FetchMixin
from src.auth.schemas import AuthenticatedUser, AuthModel, TokenPair


class LoginService(AuthInterface[TokenPair], FetchMixin):
    model_cls = TokenPair

    async def __call__(self, request: Request, user_detail: AuthModel) -> JSONResponse:  # type: ignore
        authentication_url = request.app.state.auth_settings.authentication_url
        token_pair = await self.fetch_token_pair(authentication_url, payload=user_detail.model_dump())
        return await self.create_response(token_pair)


class RefreshService(AuthInterface[TokenPair], FetchMixin):
    model_cls = TokenPair

    async def __call__(self, request: Request) -> JSONResponse:  # type: ignore
        refresh_url = request.app.state.auth_settings.refresh_token_url
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise NotAuthenticated()

        token_pair = await self.fetch_token_pair(refresh_url, cookies={"refresh_token": refresh_token})
        return await self.create_response(token_pair)


class AuthUserService(AuthInterface[AuthenticatedUser]):
    model_cls = AuthenticatedUser

    async def __call__(self, request: Request) -> AuthenticatedUser:  # type: ignore
        auth_settings = request.app.state.auth_settings
        algorithm, secret = auth_settings.ALGORITHM, auth_settings.JWT_SECRET_KEY
        cookie = request.cookies

        token = cookie.get("access_token")
        if not token:
            raise NotAuthenticated()

        try:
            payload = jwt.decode(token, key=secret, algorithms=algorithm)
        except jwt.ExpiredSignatureError:
            raise NotValidToken(detail="Token expired")
        except jwt.JWTError:
            raise NotValidToken(detail="Invalid token")
        user_data = ast.literal_eval(payload["sub"])
        return self.model_cls.model_validate(user_data)
