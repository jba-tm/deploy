from typing import TYPE_CHECKING
from fastapi.encoders import jsonable_encoder

from app.db.repository import CRUDBase
from app.utils.file import save_file, delete_file
from .models import Protocol, ProtocolStep, ProtocolFile

if TYPE_CHECKING:
    from fastapi import UploadFile
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.contrib.protocol import FileType


class CRUDProtocol(CRUDBase[Protocol]):
    pass


class CRUDProtocolStep(CRUDBase[ProtocolStep]):
    pass


class CRUDProtocolFile(CRUDBase[ProtocolFile]):
    async def create_with_file(
            self,
            async_db: "AsyncSession",
            obj_in: dict,
            upload_file: "UploadFile",
            file_type: "FileType",
    ) -> ProtocolFile:
        data = jsonable_encoder(obj_in, custom_encoder={Choices: lambda x: x.value})
        original_file = save_file(upload_file, file_dir=file_type.value)
        try:
            data = data | {
                'file_type': file_type.value,
                'file_path': original_file,
            }
            db_obj = await self.create(async_db, obj_in=data)

        except Exception as e:
            delete_file(original_file)
            raise e
        return db_obj

    async def update_with_file(
            self,
            async_db: "AsyncSession",
            db_obj: ProtocolFile,
            obj_in: dict,
            upload_file: "UploadFile",
            file_type: "FileType",
    ):
        new_file_path = save_file(upload_file, file_dir=file_type.value)
        old_file_path = db_obj.file_path
        obj_in['file_path'] = new_file_path
        try:
            db_obj = await self.update(async_db, db_obj=db_obj, obj_in=obj_in)
        except Exception as e:
            delete_file(new_file_path)
            raise e
        else:
            delete_file(old_file_path)
        return db_obj

    async def delete_with_file(self, async_db: "AsyncSession", db_obj: ProtocolFile) -> ProtocolFile:
        file_path = db_obj.file_path
        await self.delete(async_db, db_obj=db_obj)
        delete_file(file_path)
        return db_obj


protocol_repo = CRUDProtocol(Protocol)
protocol_step_repo = CRUDProtocolStep(ProtocolStep)
protocol_file_repo = CRUDProtocolFile(ProtocolFile)
