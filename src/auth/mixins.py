import aiohttp
from aiohttp import ClientConnectorError
from fastapi import HTTPException
from starlette import status
from starlette.responses import JSONResponse

from src.auth.schemas import TokenPair


class FetchMixin:
    model_cls = TokenPair

    async def fetch_token_pair(
        self, url: str, *, payload: dict | None = None, cookies: dict | None = None
    ) -> TokenPair:
        async with aiohttp.ClientSession(cookies=cookies) as session:
            try:
                async with session.post(url, json=payload, headers={"Content-Type": "application/json"}) as response:
                    auth_response = await response.json()
            except ClientConnectorError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth service unavailable right now"
                )

        if response.status in [403, 404]:
            raise HTTPException(status_code=response.status, detail=auth_response["detail"])
        return self.model_cls(**auth_response)

    @staticmethod
    async def create_response(token_pair: TokenPair) -> JSONResponse:
        response = JSONResponse(content=token_pair.model_dump())
        response.set_cookie(
            key="access_token",
            value=token_pair.access_token,
        )
        response.set_cookie(key="refresh_token", value=token_pair.refresh_token, httponly=True)
        return response
