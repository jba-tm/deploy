from app.db.repository import CRUDBase

from .models import User, FileInfo, PineconeApiInfo


class CRUDUser(CRUDBase[User]):
    pass


class CRUDFileInfo(CRUDBase[FileInfo]):
    pass


class CRUDPineconeApiInfo(CRUDBase[PineconeApiInfo]):
    pass


user_repo = CRUDUser(User)
file_info_repo = CRUDFileInfo(FileInfo)
pinecone_api_info_repo = CRUDPineconeApiInfo(PineconeApiInfo)
