from typing import Optional, Literal
from uuid import UUID
from fastapi import APIRouter, Depends,  HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.routers.dependency import get_async_db, get_commons, get_active_user
from app.core.schema import IResponseBase, IPaginationDataBase, CommonsModel
from app.contrib.account.models import User

from .repository import chat_favorite_repo, chat_repo, chat_item_repo
from .schema import (
    ChatBase, ChatCreate, ChatVisible,
    ChatItemVisible, ChatItemBase, ChatItemCreate,
    ChatFavoriteBase, ChatFavoriteCreate, ChatFavoriteVisible
)

api = APIRouter()


@api.get('/', name='chat-list', response_model=IPaginationDataBase[ChatVisible])
async def retrieve_chat_list(
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),
        order_by: Optional[Literal[
            "id", "-id"
        ]] = "-id",
):
    q = {"user_id": user.id}
    obj_list = await chat_repo.get_all(
        async_db=async_db,
        limit=commons.limit,
        offset=commons.offset,
        order_by=(order_by,),
        q=q
    )
    if commons.with_count:
        count = await chat_repo.count(async_db, params=q)
    else:
        count = None
    return {
        'page': commons.page,
        'limit': commons.limit,
        "count": count,
        "rows": obj_list
    }


@api.post(
    "/create/", name='chat-create', response_model=IResponseBase[ChatVisible],
    status_code=HTTP_201_CREATED
)
async def create_chat(
        obj_in: ChatCreate,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
):
    data = {
        "user_id": user.id,
        # "title":
    }
    result = await chat_repo.create(async_db, obj_in=obj_in)
    return {
        'message': "Created successfully",
        'data': result
    }


@api.get('/{obj_id}/detail/', name="chat-detail", response_model=ChatVisible)
async def get_single_chat(
        obj_id: UUID,
        async_db: AsyncSession = Depends(get_async_db)
):
    return await chat_repo.get(async_db, obj_id=obj_id)


@api.patch("/{obj_id}/update/", name="chat-update", response_model=IResponseBase[ChatVisible])
async def update_chat(
        obj_id: UUID,
        obj_in: ChatBase,
        async_db: AsyncSession = Depends(get_async_db)
) -> dict:
    db_obj = await chat_repo.get(async_db, obj_id=obj_id)

    result = await chat_repo.update(async_db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True))
    return {
        "message": "Chat Updated successfully",
        "data": result
    }



@api.get('/{obj_id}/delete/', name='chat-delete', response_model=IResponseBase[ChatVisible])
async def delete_chat(
        obj_id: UUID,
        async_db: AsyncSession = Depends(get_async_db)

) -> dict:
    db_obj = await chat_repo.get(async_db, obj_id=obj_id)
    try:
        await chat_repo.delete(async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Chat can't be deleted")
    return {
        "message": "Chat deleted successfully",
        "data": db_obj
    }


@api.get('/favorite/', name='chat-favorite-list', response_model=IPaginationDataBase[ChatFavoriteVisible])
async def retrieve_chat_favorite_list(
        async_db: AsyncSession = Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),
        order_by: Optional[Literal[
            "id", "-id"
        ]] = "-id"
) -> dict:
    obj_list = await chat_favorite_repo.get_all(
        async_db=async_db,
        limit=commons.limit,
        offset=commons.offset,
        order_by=(order_by,),
    )
    if commons.with_count:
        count = await chat_favorite_repo.count(async_db)
    else:
        count = None
    return {
        'page': commons.page,
        'limit': commons.limit,
        "count": count,
        "rows": obj_list
    }


@api.post('/favorite/create/', name='chat-favorite-create', response_model=IResponseBase[ChatFavoriteVisible])
async def create_chat_favorite(
        obj_in: ChatFavoriteCreate,
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    result = await chat_favorite_repo.create(async_db, obj_in=obj_in)
    return {
        "message": "Chat favorite created",
        "data": result
    }


@api.get('/favorite/{obj_id}/detail/', name='chat-favorite-detail', response_model=ChatFavoriteVisible)
async def retrieve_single_chat_favorite(
        obj_id: UUID,
        async_db: AsyncSession = Depends(get_async_db),

):
    return await chat_favorite_repo.get(async_db, obj_id=obj_id)


@api.patch('/favorite/{obj_id}/update/', name='chat-favorite-update', response_model=IResponseBase[ChatFavoriteVisible])
async def update_chat_favorite(
        obj_id: UUID,
        obj_in: ChatFavoriteBase,
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    db_obj = await chat_favorite_repo.get(async_db, obj_id=obj_id)
    result = await chat_favorite_repo.update(async_db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True))
    return {
        "message": "Chat favorite updated",
        "data": result
    }


@api.get('/favorite/{obj_id}/delete/', name='chat-favorite-delete', response_model=IResponseBase[ChatFavoriteVisible])
async def delete_chat(
        obj_id: UUID,
        async_db: AsyncSession = Depends(get_async_db)
) -> dict:
    db_obj = await chat_favorite_repo.get(async_db, obj_id=obj_id)
    try:

        await chat_favorite_repo.delete(async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Chat favorite can't be deleted")
    return {
        "message": "Chat favorite deleted successfully",
        "data": db_obj
    }
