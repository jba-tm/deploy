from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from fastapi_pagination import pagination_ctx
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, desc

from app.core.schema import IResponseBase
from app.routers.dependency import get_active_user, get_async_db, get_db

from .models import PineconeApiInfo
from .schema import (
    PineconeApiInfoVisible, PineconeApiInfoCreate, PineconeApiInfoBase
)
from .repository import pinecone_api_info_repo

CustomizedCursorPage = CustomizedPage[
    CursorPage,
    UseParamsFields(size=10),
]

api = APIRouter()


@api.get(
    '/',
    name='pinecone-list',
    response_model=CustomizedCursorPage[PineconeApiInfoVisible],
    dependencies=[Depends(pagination_ctx(CustomizedCursorPage[PineconeApiInfoVisible]))],
)
def retrieve_pinecone_list(
        user=Depends(get_active_user),
        db=Depends(get_db),
        search: Optional[str] = Query(None),
):
    # Query to select chats joining with the latest chat items
    stmt = select(PineconeApiInfo)
    if search:
        stmt = stmt.filter(PineconeApiInfo.name.ilike(f"%{search}%"))
    stmt = stmt.order_by(desc(PineconeApiInfo.id))
    return paginate(db, stmt)


@api.post('/create/', name="pinecone-create", response_model=IResponseBase[PineconeApiInfoVisible])
async def create_pinecone_api_info(
        obj_in: PineconeApiInfoCreate,
        user=Depends(get_active_user),
        async_db=Depends(get_async_db),
):
    data = {
        'user_id': user.id,
        "key": obj_in.key,
        "name": obj_in.name,
        "env": obj_in.env
    }
    result = await pinecone_api_info_repo.create(async_db, obj_in=data)
    return {
        "message": "Pinecone api info created",
        "data": result
    }


@api.delete("/{obj_id}/delete/", name="pinecone-delete", status_code=204)
async def delete_pinecone(

        obj_id: int,
        user=Depends(get_active_user),
        async_db=Depends(get_async_db),
):
    await async_db.remove(async_db, expressions=(PineconeApiInfo.id == obj_id,))
