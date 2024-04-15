from typing import Optional, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, lazyload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, desc, distinct, func

from fastapi_pagination import pagination_ctx
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.customization import CustomizedPage, UseParamsFields

from app.routers.dependency import get_async_db, get_commons, get_active_user, get_db
from app.core.schema import IResponseBase, IPaginationDataBase, CommonsModel
from app.contrib.account.models import User
from app.contrib.history.repository import ai_history_repo
from app.contrib.history import SubjectChoices, EntityChoices

from .models import (
    ChatItem, ChatItemBody, Chat, ChatItemAnswer,
)
from .repository import (
    chat_repo, chat_item_repo, chat_item_body_repo, chat_item_answer_repo
)
from .schema import (
    ChatBase, ChatVisible,
    ChatItemVisible, ChatItemCreate,
)
from .utils import retrieve_ai_answer

CustomizedCursorPage = CustomizedPage[
    CursorPage,
    UseParamsFields(size=10),
]
api = APIRouter()


@api.get(
    '/', name='chat-list', response_model=CustomizedCursorPage[ChatVisible],
    dependencies=[Depends(pagination_ctx(CustomizedCursorPage[ChatVisible]))],
)
async def retrieve_chat_list(
        user: User = Depends(get_active_user),
        db: Session = Depends(get_db),
):
    subq = (
        select(ChatItem.chat_id, func.max(ChatItem.created_at).label("max_created_at"))
        .join(Chat, Chat.id == ChatItem.chat_id)
        .filter(ChatItem.user_id == user.id)
        .group_by(ChatItem.chat_id)
        .alias()
    )

    # Query to select chats joining with the latest chat items
    stmt = (
        select(Chat)
        .join(subq, subq.c.chat_id == Chat.id)
        .join(ChatItem, (ChatItem.chat_id == subq.c.chat_id) & (ChatItem.created_at == subq.c.max_created_at))
        .order_by(desc(subq.c.max_created_at))
    )
    return paginate(db, stmt)


@api.post(
    '/create/item/', name='chat-create-item', response_model=IResponseBase[ChatVisible],
    status_code=HTTP_201_CREATED,
)
async def create_chat_item(
        obj_in: ChatItemCreate,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
) -> dict:
    result, is_error = retrieve_ai_answer(obj_in.body)
    if is_error:
        print(result)
        raise HTTPException(detail="Something went wrong!", status_code=400)
    try:
        chat = Chat(user_id=user.id, title=obj_in.body[0:250])
        async_db.add(chat)
        await async_db.flush()
        chat_item = ChatItem(
            user_id=user.id,
            chat_id=chat.id
        )
        async_db.add(chat_item)
        await async_db.flush()
        chat_item_body = ChatItemBody(
            item_id=chat_item.id,
            body=obj_in.body
        )
        async_db.add(chat_item_body)
        await async_db.flush()
        answer = ChatItemAnswer(
            body_id=chat_item_body.id,
            answer=result
        )
        async_db.add(answer)
        await async_db.commit()
        await ai_history_repo.create(async_db, obj_in={
            "user_id": user.id,
            "entity": EntityChoices.CHAT_Q_A,
            "subject_type": SubjectChoices.CHAT_Q_A_ROOM_CREATED,
        })
        return {
            "message": "Chat item created",
            "data": {
                "id": chat.id,
                "title": chat.title,
                "created_at": chat.created_at,
                "is_favorite": chat.is_favorite,
                "items": [
                    {
                        "id": chat_item.id,
                        "body": [
                            {
                                "id": chat_item_body.id,
                                "body": chat_item_body.body,
                                "created_at": chat_item_body.created_at,
                                "answers": [
                                    {
                                        "id": answer.id,
                                        "answer": answer.answer,
                                        "created_at": answer.created_at
                                    }
                                ]
                            }
                        ],
                        "created_at": chat_item.created_at,
                    }
                ]
            }
        }
    except Exception as e:
        print(e)
        await async_db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong!")


@api.get('/{obj_id}/favorite/', name="chat-favorite", response_model=IResponseBase[ChatVisible])
async def add_chat_to_favorite(

        obj_id: UUID,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
):
    db_obj = await chat_repo.get_by_params(async_db, params={
        "id": obj_id, "user_id": user.id
    })
    if db_obj.is_favorite:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Chat also on favorite")
    result = await chat_repo.update(async_db, db_obj=db_obj, obj_in={"is_favorite": True})
    return {
        "data": result,
        "message": "Chat add to favorite"
    }


@api.get('/{obj_id}/un-favorite/', name="chat-un-favorite", response_model=IResponseBase[ChatVisible])
async def add_chat_to_favorite(

        obj_id: UUID,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
):
    db_obj = await chat_repo.get_by_params(async_db, params={
        "id": obj_id, "user_id": user.id
    })
    if not db_obj.is_favorite:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Chat also on non favorite")
    result = await chat_repo.update(async_db, db_obj=db_obj, obj_in={"is_favorite": False})
    return {
        "data": result,
        "message": "Chat removed from favorites"
    }


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
    response_model=CustomizedCursorPage[ChatItemVisible],
    dependencies=[Depends(pagination_ctx(CustomizedCursorPage[ChatItemVisible]))],
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
    await ai_history_repo.create(
        async_db, obj_in={
            "user_id": user.id,
            "entity": EntityChoices.CHAT_Q_A,
            "subject_type": SubjectChoices.CHAT_Q_A_QUERY
        }
    )
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


@api.get(
    "/favorite/", name="chat-favorite-list",
    response_model=IPaginationDataBase[ChatVisible]
)
async def retrieve_chat_favorite_list(
        user=Depends(get_active_user),
        async_db=Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),
        order_by: Optional[Literal[
            "created_at", "-created_at"
        ]] = "-created_at",
):
    obj_list = await chat_repo.get_all(
        async_db=async_db,
        limit=commons.limit,
        offset=commons.offset,
        order_by=(order_by,),
        q={'user_id': user.id, "is_favorite": True}
    )
    if commons.with_count:
        count = await chat_repo.count(async_db)
    else:
        count = None
    return {
        'page': commons.page,
        'limit': commons.limit,
        "count": count,
        "rows": obj_list
    }
