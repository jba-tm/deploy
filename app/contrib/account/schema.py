from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel as PydanticBaseModel, Field, EmailStr, field_validator

from app.core.schema import BaseModel, VisibleBase
from app.contrib.account import GenderChoices


class ProfilePasswordIn(BaseModel):
    old_password: str = Field(..., alias='oldPassword', max_length=50)
    password_confirm: str = Field(..., alias='passwordConfirm', max_length=50)
    password: str = Field(max_length=50, min_length=5)

    @field_validator('password')
    def validate_password(cls, v: Optional[str], info):
        """
        Validate password
        :param v:
        :param info:
        :return:
        """
        values = info.data
        password_confirm = values.get('password_confirm')
        if v != password_confirm:
            raise ValueError('Passwords do not match')
        return v


class UserBase(BaseModel):
    email: EmailStr = Field(alias="email")
    name: str = Field(max_length=255)
    gender: Optional[GenderChoices] = None
    birthday: Optional[datetime] = None
    signature: str = Field(max_length=255)
    description: str = Field(max_length=500)


class UserCreate(UserBase):
    email: EmailStr = Field(..., alias="email")

    name: str = Field(..., max_length=255)
    password: str = Field(..., max_length=50, min_length=8)
    signature: str = Field(..., max_length=255)
    description: str = Field(..., max_length=500)


class UserVisible(VisibleBase):
    id: UUID
    email: str
    name: str
    gender: Optional[GenderChoices] = None
    signature: str
    description: str
    birthday: Optional[datetime] = None
    created_at: datetime = Field(alias="createdAt")


class FileInfoVisible(VisibleBase):
    id: int
    file_name: str = Field(alias="fileName")
    file: str
    created_at: datetime = Field(alias="createdAt")


class PineconeApiInfoBase(BaseModel):
    name: str = Field(max_length=255)
    env: str = Field(max_length=255)
    key: str = Field(max_length=255)


class PineconeApiInfoCreate(PineconeApiInfoBase):
    name: str = Field(..., max_length=255)
    env: str = Field(..., max_length=255)
    key: str = Field(..., max_length=255)


class PineconeApiInfoVisible(VisibleBase):
    id: int
    name: str
    key: str
    env: str


class Token(BaseModel):
    user: UserVisible
    token_type: str
    access_token: str
    refresh_token: Optional[str] = None


class TokenPayload(PydanticBaseModel):
    user_id: UUID
    iat: Optional[int] = None
    exp: int
    aud: str


class RefreshTokenPayload(BaseModel):
    user_id: UUID
    # jti: UUID
    iat: Optional[int] = None
    exp: int


class RefreshToken(BaseModel):
    refresh_token: str
    payload: RefreshTokenPayload


class VerifyToken(BaseModel):
    access_token: Optional[str] = Field(None)
    refresh_token: Optional[str] = Field(None)


class SignUpResult(VisibleBase):
    user: UserVisible
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class SignUpIn(BaseModel):
    name: str = Field(..., alias='name')
    email: EmailStr
    password_confirm: str = Field(..., alias='passwordConfirm')
    password: str = Field(max_length=50, min_length=5)

    @field_validator('password')
    def validate_password(cls, v: Optional[str], info):
        """
        Validate password
        :param v:
        :param info:
        :return:
        """
        values = info.data
        password_confirm = values.get('password_confirm')
        if v != password_confirm:
            raise ValueError('Passwords do not match')
        return v


class ProfileUpdate(BaseModel):
    name: str = Field(max_length=255, alias='name', min_length=2)
    email: EmailStr
    gender: Optional[GenderChoices] = None
    birthday: Optional[datetime] = None
    signature: str = Field(max_length=255)
    description: str = Field(max_length=500)
