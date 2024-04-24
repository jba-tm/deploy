from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from fastapi_pagination import pagination_ctx
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.schema import IResponseBase, CommonsModel, IPaginationDataBase
from app.routers.dependency import get_active_user, get_async_db, get_db, get_commons
from app.utils.datetime.timezone import now
from .models import PineconeApiInfo, FileInfo
from .schema import (
    PineconeApiInfoVisible, PineconeApiInfoCreate,
    FileInfoVisible,
)
from .repository import pinecone_api_info_repo, file_info_repo

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


@api.get('/file/', name='pinecone-file-list', response_model=IPaginationDataBase[FileInfoVisible])
async def retrieve_pinecone_files(
        user=Depends(get_active_user),
        async_db=Depends(get_async_db),
        pinecone_id: Optional[int] = Query(None, alias="pineconeId"),
        commons: CommonsModel = Depends(get_commons),
        order_by: Optional[Literal[
            "created_at", "-created_at"
        ]] = "-created_at",
):
    q = {"user_id": user.id}
    if pinecone_id:
        q["pinecone_id"] = pinecone_id
    obj_list = await file_info_repo.get_all(
        async_db=async_db,
        limit=commons.limit,
        offset=commons.offset,
        order_by=(order_by,),
        q=q,
        options=[
            selectinload(FileInfo.pinecone).load_only(
                PineconeApiInfo.id, PineconeApiInfo.key,
                PineconeApiInfo.name, PineconeApiInfo.env,
                PineconeApiInfo.created_at,
            )
        ]
    )
    if commons.with_count:
        count = await file_info_repo.count(async_db, params=q)
    else:
        count = None
    return {
        'page': commons.page,
        'limit': commons.limit,
        "count": count,
        "rows": obj_list
    }


@api.post('/file/upload/', name='pinecone-file-upload', response_model=IResponseBase[FileInfoVisible])
async def upload_pinecone_file(
        upload_file: UploadFile,
        pinecone_id: int = Query(..., alias="pineconeId"),
        user=Depends(get_active_user),
        async_db=Depends(get_async_db),
):
    db_obj = await pinecone_api_info_repo.get(async_db,obj_id=pinecone_id)

    result = await file_info_repo.create_with_file(
        async_db=async_db,
        obj_in={
            "user_id": user.id,
            "pinecone_id": pinecone_id,
            "file_name": upload_file.filename if upload_file.filename else now().strftime("%Y-%m-%d_%H-%M-%S")
        },
        upload_file=upload_file,
    )
    return {
        "message": "File uploaded",
        "data": {
            "id": result.id,
            "file_name": result.file_name,
            "file": result.file,
            "created_at": result.created_at,
            "pinecone": db_obj
        }
    }


@api.get('/file/{obj_id}/extract/', name='pinecone-file-extract', response_model=IResponseBase[str])
async def pinecone_file_raw_text_extract(
        obj_id: int,
        user=Depends(get_active_user),
        async_db=Depends(get_async_db),
):
    return {
        "message": "Pinecone file raw text extracted",
        "data":""
    }
