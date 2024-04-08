from typing import Generator, Optional

from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.security import lazy_jwt_settings, OAuth2PasswordBearerWithCookie
from app.conf.config import settings
from app.contrib.account.schema import TokenPayload
from app.contrib.account.models import User

from app.contrib.account.repository import user_repo
from app.core.exceptions import HTTPUnAuthorized, HTTPInvalidToken, HTTPPermissionDenied
from app.core.schema import CommonsModel
from app.utils.jose import jwt
from app.db.session import AsyncSessionLocal, SessionLocal, gk_engine

# from app.utils.translation import gettext as _
reusable_oauth2 = OAuth2PasswordBearerWithCookie(tokenUrl=f'{settings.API_V1_STR}/auth/get-token/', auto_error=True)

def get_gk_engine():
    return gk_engine

def get_db()->Generator:
    try:
        with SessionLocal() as session:
            yield session
    finally:
        session.close()


async def get_async_db() -> Generator:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    finally:
        await session.close()


async def get_token_payload(
        token: str = Depends(reusable_oauth2),
) -> TokenPayload:
    try:
        payload = lazy_jwt_settings.JWT_DECODE_HANDLER(token)
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPUnAuthorized
    return token_data


async def get_current_user(
        token_payload: TokenPayload = Depends(get_token_payload),
        async_db: AsyncSession = Depends(get_async_db),
) -> User:
    """
    Get user by token
    :param token_payload:
    :param async_db:
    :return:
    """
    user = await user_repo.first(async_db=async_db, params={'id': token_payload.user_id})
    if not user:
        raise HTTPInvalidToken(detail="Invalid token")
    return user


async def get_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPPermissionDenied(detail=_("Your account is disabled"))
    return user


async def get_commons(
        page: Optional[int] = 1,
        limit: Optional[int] = settings.PAGINATION_MAX_SIZE,
        with_count: Optional[bool] = False,
) -> CommonsModel:
    """

    Get commons dict for list pagination
    :param limit: Optional[int] = 1
    :param page: Optional[int] = 25
    :param with_count: Optional[bool] = False
    :return:
    """
    if not page or not isinstance(page, int):
        page = 1
    elif page < 0:
        page = 1
    offset = (page - 1) * limit
    return CommonsModel(
        limit=limit,
        offset=offset,
        page=page,
        with_count=with_count,
    )


def get_language(lang: Optional[str] = settings.LANGUAGE_CODE):
    return lang
