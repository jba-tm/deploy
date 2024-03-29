from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload, load_only
from sqlalchemy import select, text
import requests

from fastapi_pagination import pagination_ctx
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import paginate

from app.core.exceptions import HTTP404
from app.conf.config import settings
from app.routers.dependency import get_async_db, get_active_user, get_db
from app.core.schema import IResponseBase
from app.contrib.account.models import User

from .utils import get_property
from .repository import protocol_repo, protocol_step_repo
from .models import Protocol, ProtocolStep
from .schema import (
    ProtocolBase, ProtocolCreate, ProtocolVisible, ProtocolSource,
    ProtocolStepVisible, ProtocolStepCreate, ProtocolStepBase
)

sources = {
    "be": settings.BE_API_URL,
    "pubmed": settings.PUBMED_API_URL,
    "ob": settings.OG_API_URL
}

api = APIRouter()
CursorPage = CursorPage.with_custom_options(size=10)


def get_protocol_prompt_content(medicine: str, step: str):
    protocol_property = get_property(medicine, step)
    if not protocol_property:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Wrong protocol step provided")

    prompt = protocol_property.get('prompt')
    source = protocol_property.get("source")

    try:
        response = requests.post(
            sources[source], json={"question": prompt}
        )
        result = response.json()
    except Exception as e:
        print(e)
        raise HTTPException(detail="Something went wrong", status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    return result.get("text", ""), prompt, source, protocol_property.get("question")


@api.get(
    "/", name="protocol-list",
    response_model=CursorPage[ProtocolVisible],
    dependencies=[Depends(pagination_ctx(CursorPage[ProtocolVisible]))],
)
async def retrieve_protocol_list(
        db: Session = Depends(get_db),
        user: User = Depends(get_active_user),
):
    stmt = select(Protocol).filter(Protocol.user_id == user.id).order_by(Protocol.created_at.desc())
    return paginate(db, stmt)


@api.post(
    '/create/', name='protocol-create', response_model=IResponseBase[ProtocolVisible],
    status_code=HTTP_201_CREATED
)
async def create_protocol(
        obj_in: ProtocolCreate,
        async_db: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_active_user),

) -> dict:
    content, prompt, source, question = get_protocol_prompt_content(obj_in.medicine, "0")
    try:
        protocol = Protocol(
            user_id=user.id,
            medicine=obj_in.medicine,
            current_step="0",
        )
        async_db.add(protocol)
        await async_db.flush()
        protocol_step = ProtocolStep(
            protocol_id=protocol.id,
            question=question,
            prompt=prompt,
            content=content,
            source=source,
            step="0",
            user_id=user.id,
        )
        async_db.add(protocol_step)
        await async_db.commit()
        await async_db.refresh(protocol)
        await async_db.refresh(protocol_step)
        # result = await protocol_repo.create(async_db, obj_in=data)
        return {
            "message": "Protocol created",
            "data": {
                "id": protocol.id,
                "medicine": protocol.medicine,
                "current_step_obj": {
                    "id": protocol_step.id,
                    "question": protocol_step.question,
                    "prompt": protocol_step.prompt,
                    "content": protocol_step.content,
                    "step": protocol_step.step,
                    "source": protocol_step.source,
                    "created_at": protocol_step.created_at,
                },
                "current_step": protocol.current_step,
                "created_at": protocol.created_at,
            }
        }
    except Exception as e:
        print(e)
        await async_db.rollback()
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong!")


@api.get('/{obj_id}/detail/', name='protocol-detail', response_model=ProtocolVisible)
async def retrieve_single_protocol(
        obj_id: UUID,
        async_db: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_active_user),
):
    sql_txt = text("""
            SELECT 
            p."id", 
            p."medicine",
            p."created_at",
            p."current_step",
            ps."id" as "ps_id",
            ps."created_at" as "ps_created_at",
            ps."question" as "ps_question",
            ps."prompt" as "ps_prompt",
            ps."content" as "ps_content",
            ps."step" as "ps_step",
            ps."source" as "ps_source"
        FROM public."protocol" p
        JOIN public."protocol_step" ps ON p."id" = ps."protocol_id" and p."current_step" = ps."step"
        WHERE p."id"=:obj_id and p."user_id"=:user_id;
    """)
    fetch = await async_db.execute(sql_txt, params={'obj_id': obj_id, "user_id": user.id})
    db_obj = fetch.fetchone()

    if not db_obj:
        raise HTTP404(detail="Protocol does not exist")
    return {
        "id": db_obj.id,
        "medicine": db_obj.medicine,
        "current_step_obj": {
            "id": db_obj.ps_id,
            "question": db_obj.ps_question,
            "prompt": db_obj.ps_prompt,
            "content": db_obj.ps_content,
            "step": db_obj.ps_step,
            "source": db_obj.ps_source,
            "created_at": db_obj.ps_created_at,
        },
        "created_at": db_obj.created_at,
        "current_step": db_obj.current_step,
    }


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
        user: User = Depends(get_active_user),
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


@api.post('/step/create/', name='protocol-step-create', response_model=IResponseBase[ProtocolStepVisible])
async def create_protocol_step(
        obj_in: ProtocolStepCreate,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    content, prompt, source, question = get_protocol_prompt_content(obj_in.medicine, obj_in.step)

    protocol = await protocol_repo.get(async_db, obj_id=obj_in.protocol_id)
    if not protocol:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid protocol id")

    try:
        data = {
            "user_id": user.id,
            "protocol_id": obj_in.protocol_id,
            "question": question,
            "prompt": prompt,
            "source": source,
            "step": obj_in.step,
            "content": content,
        }
        result = await protocol_step_repo.create(async_db, obj_in=data)
    except Exception as e:
        print(e)
        await async_db.rollback()
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")
    await protocol_repo.update(async_db, db_obj=protocol, obj_in={"current_step": result.step})
    return {
        "message": "Protocol step created",
        "data": result
    }


@api.get('/step/{obj_id}/detail/', name='protocol-step-detail', response_model=ProtocolStepVisible)
async def retrieve_protocol_step(
        obj_id: int,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
):
    return await protocol_step_repo.get_by_params(async_db, params={"user_id": user.id, "id": obj_id})


@api.post('/step/{obj_id}/update/', name="protocol-step-update", response_model=IResponseBase[ProtocolStepVisible])
async def update_protocol_step(
        obj_id: int,
        obj_in: ProtocolStepBase,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
):
    db_obj = await protocol_step_repo.get_by_params(async_db, params={"user_id": user.id, "id": obj_id})
    result = await protocol_step_repo.update(
        async_db,
        db_obj=db_obj,
        obj_in={
            "content": obj_in.content,
        }
    )

    return {
        "message": "Protocol step updated",
        "data": result,
    }


@api.get('/step/{obj_id}/refresh/', name="protocol-step-refresh", response_model=IResponseBase[ProtocolStepVisible])
async def refresh_prompt_protocol_step(
        obj_id: int,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    db_obj = await protocol_step_repo.get_by_params(
        async_db, params={"user_id": user.id, "id": obj_id},
        options=(selectinload(ProtocolStep.protocol).options(load_only(Protocol.medicine),),)
    )
    content, prompt, source, question = get_protocol_prompt_content(db_obj.protocol.medicine, db_obj.step)

    result = await protocol_step_repo.update(
        async_db, db_obj=db_obj,
        obj_in={
            "content": content
        }
    )
    return {
        "message": "Protocol step content refreshed by prompt",
        "data": result
    }


@api.post('/source/', name="protocol-source", response_model=IResponseBase[dict])
async def protocol_be_source(
        obj_in: ProtocolSource,
        user: User = Depends(get_active_user),
):
    try:
        response = requests.post(
            sources[obj_in.source_type], json={"question": obj_in.query}
        )
        return {
            "message": "Source created",
            "data": response.json()
        }
    except Exception as e:
        print(e)
        raise HTTPException(detail="Something went wrong", status_code=HTTP_500_INTERNAL_SERVER_ERROR)
