import requests

from uuid import UUID
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, load_only
from sqlalchemy import text
from docx import Document
from htmldocx import HtmlToDocx

from app.utils.datetime.timezone import today
from app.core.exceptions import HTTP404
from app.conf.config import settings, structure_settings
from app.routers.dependency import get_async_db, get_active_user, get_commons
from app.core.schema import IResponseBase, IPaginationDataBase, CommonsModel
from app.contrib.account.models import User
from app.utils.sanitizer import text_to_html_paragraphs, Sanitizer
from app.utils.file import upload_to
from app.contrib.protocol import FileType
from app.contrib.history import EntityChoices, SubjectChoices
from app.contrib.history.repository import ai_history_repo

from .utils import get_property
from .repository import protocol_repo, protocol_step_repo, protocol_file_repo
from .models import Protocol, ProtocolStep
from .schema import (
    ProtocolBase, ProtocolCreate, ProtocolVisible,
    ProtocolSource,
    ProtocolStepVisible, ProtocolStepCreate, ProtocolStepBase,
    ProtocolExtended
)

sources = {
    "be": settings.BE_API_URL,
    "pubmed": settings.PUBMED_API_URL,
    "og": settings.OG_API_URL
}

api = APIRouter()


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
        print(response.json())
        if response.status_code == 200:
            result = response.json()
        else:
            raise HTTPException(detail="Something went wrong!", status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(e)
        raise HTTPException(detail="Something went wrong!", status_code=HTTP_500_INTERNAL_SERVER_ERROR)

    html_text = text_to_html_paragraphs(result.get("text", ""))
    print(html_text, )
    return html_text, prompt, source, protocol_property.get("question")


@api.get(
    "/", name="protocol-list",
    response_model=IPaginationDataBase[ProtocolVisible]
)
async def retrieve_protocol_list(
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),
        order_by: Optional[Literal[
            "created_at", "-created_at"
        ]] = "-created_at",
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
    '/create/',
    name='protocol-create',
    response_model=IResponseBase[ProtocolExtended],
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
            step_order=0,
            user_id=user.id,
        )
        async_db.add(protocol_step)
        await async_db.commit()
        await async_db.refresh(protocol)
        await async_db.refresh(protocol_step)
        await ai_history_repo.create(async_db, obj_in={
            "user_id": user.id,
            "entity": EntityChoices.PROTOCOL,
            "subject_type": SubjectChoices.PROTOCOL_CREATED,
        })
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
                    "step_order": protocol_step.step_order,
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


@api.get('/{obj_id}/detail/', name='protocol-detail', response_model=ProtocolExtended)
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
            ps."step_order" as "ps_step_order",
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
            "step_order": db_obj.ps_step_order,
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
    result = await protocol_repo.update(
        async_db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )
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
    db_obj = await protocol_repo.get_by_params(async_db, params={"id": obj_id, "user_id": user.id})
    try:
        await protocol_repo.delete(async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Protocol can't be deleted")
    return {
        "message": "Protocol deleted",
        "data": db_obj
    }


@api.get('/{obj_id}/generate/docx/', name='protocol-gen-docx', response_model=IResponseBase[str])
async def protocol_generate_docx(
        obj_id: UUID,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
):
    db_obj = await protocol_repo.get_by_params(async_db, params={"id": obj_id, "user_id": user.id})
    is_exist = await protocol_file_repo.exists(async_db, params={'protocol_id': obj_id, "file_type": "docx"})
    if is_exist:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Protocol docx file already generated. Try to delete it first."
        )
    steps = await protocol_step_repo.get_all(
        async_db,
        q={'protocol_id': obj_id},
        limit=500,
        order_by=("step",),
        options=(load_only(ProtocolStep.content),),
    )
    html_text = ""
    for step in steps:
        html_text = html_text + step.content
    doc = Document()
    new_parser = HtmlToDocx()
    new_parser.add_html_to_document(html_text, doc)
    path = upload_to(str(obj_id), ".docx", file_dir="docx", is_protected=True)

    doc.save(f'{structure_settings.MEDIA_DIR}/{path}')
    await protocol_file_repo.create(async_db, obj_in={
        "protocol_id": db_obj.id,
        "file_path": path,
        "file_type": "docx"
    })
    await ai_history_repo.create(async_db, obj_in={
        "user_id": user.id,
        "entity": EntityChoices.PROTOCOL,
        "subject_type": SubjectChoices.PROTOCOL_FILE_GENERATED
    })

    return {
        "message": "Protocol docx file created",
        "data": ""
    }


@api.get('/{obj_id}/generate/delete/', name='protocol-file-delete', response_model=IResponseBase[str])
async def delete_protocol_docx_file(
        obj_id: UUID,
        file_type: FileType = Query(...),
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
):
    protocol = await protocol_repo.exists(async_db, params={"id": obj_id, "user_id": user.id})
    if not protocol:
        raise HTTP404(detail="Protocol does not exist")
    db_obj = await protocol_file_repo.get_by_params(
        async_db,
        params={"protocol_id": obj_id, "file_type": file_type.value}
    )
    await protocol_file_repo.delete_with_file(async_db, db_obj=db_obj)

    return {
        "message": "Protocol file deleted",
        "data": ""
    }


@api.get(
    '/{obj_id}/generate/download/', name="protocol-file-download", response_model=bytes,
    response_class=FileResponse,
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {

                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                },
                "application/pdf": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                },
            },
            "description": "Return the a docx or a pdf.",
        }
    },
)
async def protocol_download_generated(
        obj_id: UUID,
        file_type: FileType = Query(...),
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
):
    protocol = await protocol_repo.get_by_params(
        async_db, params={
            "id": obj_id,
            # "user_id": user.id
        }, options=(load_only(Protocol.medicine),))
    if not protocol:
        raise HTTP404(detail="Protocol does not exist")

    db_obj = await protocol_file_repo.get_by_params(
        async_db,
        params={"protocol_id": obj_id, "file_type": file_type.value}
    )
    # return f"{structure_settings.MEDIA_DIR}/{db_obj.file_path}"
    today_str = today().strftime("%d-%m-%y")
    if file_type == FileType.DOCX:
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        media_type = "application/pdf"
    return FileResponse(
        f"{structure_settings.PROTECTED_DIR}/{db_obj.file_path}",
        filename=f"{protocol.medicine}-{today_str}.{file_type.value}",
        media_type=media_type
    )


@api.post(
    '/step/create/',
    name='protocol-step-create',
    response_model=IResponseBase[ProtocolStepVisible],
    status_code=HTTP_201_CREATED,
)
async def create_protocol_step(
        obj_in: ProtocolStepCreate,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    is_exists = await protocol_step_repo.exists(async_db,
                                                params={"protocol_id": obj_in.protocol_id, "step": obj_in.step})
    if is_exists:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Protocol already has this step"
        )
    content, prompt, source, question = get_protocol_prompt_content(obj_in.medicine, obj_in.step)

    protocol = await protocol_repo.get(async_db, obj_id=obj_in.protocol_id)
    if not protocol:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid protocol id")

    try:
        protocol_step = ProtocolStep(
            user_id=user.id,
            protocol_id=protocol.id,
            question=question,
            prompt=prompt,
            source=source,
            step=obj_in.step,
            step_order=obj_in.step_order,
            content=content,
        )
        async_db.add(protocol_step)
        protocol.current_step = obj_in.step
        async_db.add(protocol)
        await async_db.commit()
        await async_db.refresh(protocol_step)
        return {
            "message": "Protocol step created",
            "data": protocol_step
        }
    except Exception as e:
        print(e)
        await async_db.rollback()
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")


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

    sanitizer = Sanitizer()
    data = {
        "content": sanitizer.sanitize(obj_in.content)
    }
    result = await protocol_step_repo.update(
        async_db,
        db_obj=db_obj,
        obj_in=data
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
        options=(selectinload(ProtocolStep.protocol).options(load_only(Protocol.medicine), ),)
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
