from datetime import timedelta
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic_core import ErrorDetails
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_400_BAD_REQUEST
from sqlalchemy.ext.asyncio import AsyncSession

from app.contrib.account.repository import user_repo
from app.utils.security import lazy_jwt_settings, rand_code
from app.routers.dependency import get_async_db, get_current_user, get_commons, get_active_user
from app.core.schema import IResponseBase, IPaginationDataBase, CommonsModel
from app.conf.config import settings

from .schema import (
    Token, UserVisible, UserBase, UserCreate,
    SignUpResult, SignUpIn, ProfileUpdate
)
from .models import User

api = APIRouter()


@api.post('/auth/get-token/', name='get-token', response_model=Token)
async def get_token(
        data: OAuth2PasswordRequestForm = Depends(),
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    """
    Get token from external api
    """
    user = await user_repo.authenticate(
        async_db=async_db,
        email=data.username,
        password=data.password,
    )

    if not user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="incorrect-email-password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="user-account-locked"
        )

    payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
        {
            'user_id': user.id,
            'aud': lazy_jwt_settings.JWT_AUDIENCE,
        },
    )
    jwt_token = lazy_jwt_settings.JWT_ENCODE_HANDLER(payload)

    result = {
        'access_token': jwt_token,
        'token_type': 'bearer',
        "user": user
    }
    if lazy_jwt_settings.JWT_ALLOW_REFRESH:
        refresh_payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
            {"user_id": str(user.id)},
            expires_delta=timedelta(days=lazy_jwt_settings.JWT_REFRESH_EXPIRATION_DAYS))
        refresh = lazy_jwt_settings.JWT_ENCODE_HANDLER(refresh_payload)
        result["refresh_token"] = refresh
    return result


@api.get("/auth/me/", response_model=UserVisible, name='me')
async def get_me(
        user: "User" = Depends(get_current_user)
):
    return user


@api.post('/auth/sign-up/', name='sign-up', response_model=IResponseBase[SignUpResult])
async def sign_up(
        obj_in: SignUpIn,
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    email_exist = await user_repo.exists(async_db, params={"email": obj_in.email})
    if email_exist:
        raise RequestValidationError(
            [ErrorDetails(
                msg="User with this email already exist",
                loc=("body", "email",),
                type='value_error',
                input=obj_in.email
            )]
        )
    user = await user_repo.create(
        async_db=async_db,
        obj_in={
            "email": obj_in.email,
            "name": obj_in.name,
            "password": obj_in.password,
        }
    )

    payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
        {"user_id": str(user.id)},
    )
    jwt_token = lazy_jwt_settings.JWT_ENCODE_HANDLER(payload)
    result = {"access_token": jwt_token, "token_type": "bearer", "user": user}

    if lazy_jwt_settings.JWT_ALLOW_REFRESH:
        refresh_payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
            {"user_id": str(user.id)},
            expires_delta=lazy_jwt_settings.JWT_REFRESH_EXPIRATION_DELTA
        )
        refresh = lazy_jwt_settings.JWT_ENCODE_HANDLER(refresh_payload)
        result["refresh_token"] = refresh
    # generated_code = rand_code(settings.VERIFICATION_CODE_LENGTH)

    return {
        "data": result,
        "message": "Email confirmation sent to your email: %(email)s" % {"email": obj_in.email}
    }


@api.patch("/profile/update/", name="user-profile-update", response_model=IResponseBase[UserVisible])
async def user_profile_update(
        obj_in: ProfileUpdate,
        user: User = Depends(get_current_user),

        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    result = await user_repo.update(
        asynb_db=async_db,
        db_obj=user,
        obj_in=obj_in.dict(exclude_unset=True)
    )
    return {
        "message": "Profile updated",
        "data": result
    }
