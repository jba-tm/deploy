from typing import TYPE_CHECKING, Optional
from fastapi.encoders import jsonable_encoder

from app.db.repository import CRUDBase
from app.utils.file import save_file, delete_file
from app.core.enums import Choices

from .models import FileInfo, PineconeApiInfo

if TYPE_CHECKING:
    from fastapi import UploadFile
    from sqlalchemy.ext.asyncio import AsyncSession


class CRUDFileInfo(CRUDBase[FileInfo]):
    async def create_with_file(
            self,
            async_db: "AsyncSession",
            upload_file: "UploadFile",
            obj_in: Optional[dict] = None,
    ) -> "FileInfo":
        if obj_in is None:
            obj_in = dict()
        data = jsonable_encoder(obj_in, custom_encoder={Choices: lambda x: x.value})
        original_file = save_file(upload_file, file_dir="pinecone", is_protected=True)
        try:
            data["file"] = original_file
            db_obj = await self.create(async_db, obj_in=data)
        except Exception as e:
            delete_file(original_file, True)
            raise e
        return db_obj

    async def update_with_file(
            self,
            async_db: "AsyncSession",
            db_obj: FileInfo,
            obj_in: dict,
            upload_file: "UploadFile",
    ):
        new_image_path = save_file(upload_file, file_dir="pinecone", is_protected=True)
        old_image_path = db_obj.media_path
        obj_in['file'] = new_image_path
        try:
            db_obj = await self.update(async_db, db_obj=db_obj, obj_in=obj_in)
        except Exception as e:
            delete_file(new_image_path, is_protected=True)
            raise e
        else:
            delete_file(old_image_path, is_protected=True)
        return db_obj

    async def delete_with_file(self, async_db: "AsyncSession", db_obj: FileInfo) -> FileInfo:
        file_path = db_obj.file
        await self.delete(async_db, db_obj=db_obj)
        delete_file(file_path, is_protected=True)
        return db_obj


class CRUDPineconeApiInfo(CRUDBase[PineconeApiInfo]):
    pass


file_info_repo = CRUDFileInfo(FileInfo)
pinecone_api_info_repo = CRUDPineconeApiInfo(PineconeApiInfo)
