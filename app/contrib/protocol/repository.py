from app.db.repository import CRUDBase

from .models import Protocol, ProtocolStep


class CRUDProtocol(CRUDBase[Protocol]):
    pass


class CRUDProtocolStep(CRUDBase[ProtocolStep]):
    pass


protocol_repo = CRUDProtocol(Protocol)
protocol_step_repo = CRUDProtocolStep(ProtocolStep)
