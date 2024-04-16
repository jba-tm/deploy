from app.db.repository import CRUDBase

from .models import FileInfo, PineconeApiInfo


class CRUDFileInfo(CRUDBase[FileInfo]):
    pass


class CRUDPineconeApiInfo(CRUDBase[PineconeApiInfo]):
    pass


file_info_repo = CRUDFileInfo(FileInfo)
pinecone_api_info_repo = CRUDPineconeApiInfo(PineconeApiInfo)
