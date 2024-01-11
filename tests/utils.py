from datetime import datetime, timedelta

from jose import jwt

from core.config.auth_settings import AuthSettings
from src.auth.schemas import AuthenticatedUser


def create_access_token(auth_settings: AuthSettings, auth_user: AuthenticatedUser, exp_time: int | None = None) -> str:
    exp_time = exp_time or 60
    expires_delta = datetime.utcnow() + timedelta(minutes=exp_time)
    to_encode = {"exp": expires_delta, "sub": str(auth_user.model_dump())}
    encoded_jwt = jwt.encode(to_encode, auth_settings.JWT_SECRET_KEY, auth_settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(auth_settings: AuthSettings, auth_user: AuthenticatedUser, exp_time: int | None = None) -> str:
    exp_time = exp_time or 60
    expires_delta = datetime.utcnow() + timedelta(minutes=exp_time)

    to_encode = {"exp": expires_delta, "sub": str(auth_user.model_dump())}
    encoded_jwt = jwt.encode(
        to_encode,
        auth_settings.JWT_REFRESH_SECRET_KEY,
        auth_settings.ALGORITHM,
    )
    return encoded_jwt
