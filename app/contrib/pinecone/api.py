from fastapi import APIRouter, Depends
from app.core.schema import IResponseBase
from app.routers.dependency import get_active_user, get_async_db

from .schema import (
    PineconeApiInfoVisible, PineconeApiInfoCreate, PineconeApiInfoBase
)
from .repository import pinecone_api_info_repo

api = APIRouter()


@api.post('/create/', name="pinecone-info-create", response_model=IResponseBase[PineconeApiInfoVisible])
async def create_pinecone_api_info(
        obj_in: PineconeApiInfoCreate,
        user=Depends(get_active_user),
        async_db=Depends(get_async_db),
):
    result = await pinecone_api_info_repo.create(async_db, obj_in=obj_in)
    return {
        "message": "Pinecone api info created",
        "data": result
    }

