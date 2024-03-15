from app.db.repository import CRUDBase

from .models import Protocol


class CRUDProtocol(CRUDBase):
    pass


protocol_repo = CRUDProtocol(Protocol)
