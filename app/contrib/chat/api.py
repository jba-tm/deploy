from typing import Optional, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, lazyload, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from fastapi_pagination import pagination_ctx
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import paginate

from app.routers.dependency import get_async_db, get_commons, get_active_user, get_db
from app.core.schema import IResponseBase, IPaginationDataBase, CommonsModel
from app.contrib.account.models import User

from .models import ChatItem, ChatItemBody, Chat
from .repository import (
    chat_favorite_repo, chat_repo, chat_item_repo, chat_item_body_repo, chat_item_answer_repo
)
from .schema import (
    ChatBase, ChatCreate, ChatVisible,
    ChatItemVisible, ChatItemBase, ChatItemCreate,
    ChatFavoriteBase, ChatFavoriteCreate, ChatFavoriteVisible
)
from .utils import retrieve_ai_answer

CursorPage = CursorPage.with_custom_options(size=10)

api = APIRouter()


@api.get(
    '/', name='chat-list', response_model=CursorPage[ChatVisible],
    dependencies=[Depends(pagination_ctx(CursorPage[ChatVisible]))],
)
async def retrieve_chat_list(
        user: User = Depends(get_active_user),
        db: Session = Depends(get_db),
):
    stmt = select(Chat).filter(Chat.user_id == user.id).order_by(Chat.created_at.desc())
    return paginate(db, stmt)


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
        "title": obj_in.title,
    }
    result = await chat_repo.create(async_db, obj_in=data)
    return {
        'message': "Created successfully",
        'data': result
    }


@api.post('/create/item/', name='chat-create-item', response_model=IResponseBase[ChatVisible])
async def create_chat_item(
        obj_in: ChatItemCreate,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
) -> dict:
    result, is_error = retrieve_ai_answer(obj_in.body)
    if is_error:
        raise HTTPException(detail="Something went wrong!", status_code=400)

    chat = await chat_repo.create(async_db, obj_in={
        "user_id": user.id,
        "title": "Test chat title",
    })
    chat_item = await chat_item_repo.create(
        async_db=async_db,
        obj_in={
            "user_id": user.id,
            "chat_id": chat.id,
        })
    chat_item_body = await chat_item_body_repo.create(
        async_db,
        obj_in={
            "item_id": chat_item.id,
            "body": obj_in.body,
        }
    )
    answer = await chat_item_answer_repo.create(
        async_db,
        obj_in={
            "body_id": chat_item_body.id,
            "answer": result
        }
    )
    return {
        "message": "Chat item created",
        "data": {
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at,
            "items": [
                {
                    "id": chat_item.id,
                    "body": [
                        {
                            "id": chat_item_body.id,
                            "body": chat_item_body.body,
                            "created_at": chat_item_body.created_at,
                            "answers": [
                                {"id": answer.id, "answer": answer.answer, "created_at": answer.created_at}
                            ]
                        }
                    ],
                    "created_at": chat_item.created_at,
                }
            ]}}


@api.get('/{obj_id}/detail/', name="chat-detail", response_model=ChatVisible)
async def get_single_chat(
        obj_id: UUID,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
):
    db_obj = await chat_repo.get_by_params(async_db, params={
        "id": obj_id, "user_id": user.id
    })
    return db_obj


@api.patch("/{obj_id}/update/", name="chat-update", response_model=IResponseBase[ChatVisible])
async def update_chat(
        obj_id: UUID,
        obj_in: ChatBase,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
) -> dict:
    db_obj = await chat_repo.get_by_params(async_db, params={
        "id": obj_id, "user_id": user.id
    })
    result = await chat_repo.update(async_db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True))
    return {
        "message": "Chat Updated successfully",
        "data": result
    }


@api.get('/{obj_id}/delete/', name='chat-delete', response_model=IResponseBase[ChatVisible])
async def delete_chat(
        obj_id: UUID,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)

) -> dict:
    db_obj = await chat_repo.get_by_params(async_db, params={
        "id": obj_id, "user_id": user.id
    })
    try:
        await chat_repo.delete(async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Chat can't be deleted")
    return {
        "message": "Chat deleted successfully",
        "data": db_obj
    }


@api.get(
    "/{obj_id}/items/", name='chat-item-list',
    response_model=CursorPage[ChatItemVisible],
    dependencies=[Depends(pagination_ctx(CursorPage[ChatItemVisible]))],
)
async def chat_item_list(
        obj_id: UUID,
        user: User = Depends(get_active_user),
        db: Session = Depends(get_db),
):
    stmt = select(ChatItem).options(
        lazyload(ChatItem.body).lazyload(ChatItemBody.answers),
    ).join(ChatItem.body).join(ChatItemBody.answers).filter(
        ChatItem.chat_id == obj_id, ChatItem.user_id == user.id
    ).order_by(ChatItem.id.desc())
    return paginate(db, stmt)


@api.post('/{obj_id}/items/add/', name='chat-item-add', response_model=IResponseBase[ChatItemVisible])
async def chat_item_add(
        obj_id: UUID,
        obj_in: ChatItemCreate,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),

) -> dict:
    chat = await chat_repo.get_by_params(async_db, params={'user_id': user.id, "id": obj_id})
    ai_result, is_error = retrieve_ai_answer(question=obj_in.body)
    if is_error:
        raise HTTPException(detail="Something went wrong!", status_code=400)
    chat_item = await chat_item_repo.create(async_db, obj_in={"user_id": user.id, 'chat_id': chat.id})
    question = await chat_item_body_repo.create(async_db, obj_in={'item_id': chat_item.id, "body": obj_in.body})
    answer = await chat_item_answer_repo.create(async_db, obj_in={'body_id': question.id, "answer": ai_result})
    return {
        "message": "Chat item created",
        "data": {

            "id": chat_item.id,
            "body": [
                {
                    "id": question.id,
                    "body": question.body,
                    "created_at": question.created_at,
                    "answers": [
                        {"id": answer.id, "answer": answer.answer, "created_at": answer.created_at}
                    ]
                }
            ],
            "created_at": chat_item.created_at,
        }
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
