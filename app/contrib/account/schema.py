from datetime import datetime
from typing import Optional

from pydantic import BaseModel as PydanticBaseModel, Field, EmailStr

from app.core.schema import BaseModel, VisibleBase

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserVisible


class TokenPayload(PydanticBaseModel):
    user_id: int
    iat: Optional[int] = None
    exp: int
    aud: str


class VerifyToken(PydanticBaseModel):
    access_token: Optional[str] = Field(None)
