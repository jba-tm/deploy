from typing import Generic, Optional, TypeVar, List, Union, Type, Any
from pydantic import (
    BaseModel as PydanticBaseModel, ConfigDict, Field,

)
from typing_extensions import Annotated
from pydantic_core import PydanticCustomError, core_schema

from pydantic.functional_serializers import WrapSerializer

from app.conf.config import settings

DataType = TypeVar("DataType")


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )


class IResponseBase(PydanticBaseModel, Generic[DataType]):
    message: Optional[str] = None
    data: DataType

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class IPaginationDataBase(PydanticBaseModel, Generic[DataType]):
    count: int
    limit: int
    page: int
    rows: List[DataType]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class CommonsModel(PydanticBaseModel):
    limit: Optional[int] = settings.PAGINATION_MAX_SIZE
    offset: Optional[int] = 0
    page: Optional[int] = 1


class VisibleBase(PydanticBaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class ChoiceBase(PydanticBaseModel):
    value: Union[str, int]
    label: str


def ser_choice(v, nxt) -> dict:
    return {
        "value": v.value,
        "label": str(v.label)
    }


FancyChoice = Annotated[ChoiceBase, WrapSerializer(ser_choice, when_used='json')]


class PhoneNumberExtendedModel(PydanticBaseModel):
    phone: str
    country_code: int = Field(alias='countryCode')
    national_number: int = Field(alias='nationalNumber')

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )
