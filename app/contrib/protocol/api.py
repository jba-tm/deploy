from typing import Optional, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.routers.dependency import get_async_db, get_commons
from app.core.schema import IResponseBase, IPaginationDataBase, CommonsModel

from .repository import protocol_repo
from .schema import ProtocolBase, ProtocolCreate, ProtocolVisible

api = APIRouter()


@api.get("/", name="protocol-list", response_model=IPaginationDataBase[ProtocolVisible])
async def retrieve_protocol_list(
        async_db: AsyncSession = Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),
        order_by: Optional[Literal[
            "id", "-id"
        ]] = "-id",
):
    obj_list = await protocol_repo.get_all(
        async_db=async_db,
        limit=commons.limit,
        offset=commons.offset,
        order_by=(order_by,),
    )
    if commons.with_count:
        count = await protocol_repo.count(async_db)
    else:
        count = None
    return {
        'page': commons.page,
        'limit': commons.limit,
        "count": count,
        "rows": obj_list
    }


@api.post(
    '/create/', name='protocol-create', response_model=IResponseBase[ProtocolVisible],
    status_code=HTTP_201_CREATED
)
async def create_protocol(
        obj_in: ProtocolCreate,
        async_db: AsyncSession = Depends(get_async_db),

) -> dict:
    result = await protocol_repo.create(async_db, obj_in=obj_in)
    return {
        "message": "Protocol created",
        "data": result
    }


@api.get('/{obj_id}/detail/', name='protocol-detail', response_model=ProtocolVisible)
async def retrieve_single_protocol(
        obj_id: UUID,
        async_db: AsyncSession = Depends(get_async_db),

):
    return await protocol_repo.get(async_db, obj_id=obj_id)


@api.patch('/{obj_id}/update/', name='protocol-update', response_model=IResponseBase[ProtocolVisible])
async def update_protocol(

        obj_id: UUID,
        obj_in: ProtocolBase,
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    db_obj = await protocol_repo.get(async_db, obj_id=obj_id)
    result = await protocol_repo.update(async_db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True))
    return {
        'message': "Protocol updated",
        "data": result
    }


@api.get('/{obj_id}/delete/', name='protocol-delete', response_model=IResponseBase[ProtocolVisible])
async def delete_protocol(

        obj_id: UUID,
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    db_obj = await protocol_repo.get(async_db, obj_id=obj_id)
    try:
        await protocol_repo.delete(async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Protocol can't be deleted")
    return {
        "message": "Protocol deleted",
        "data": db_obj
    }
