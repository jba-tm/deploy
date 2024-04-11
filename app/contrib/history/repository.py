from app.db.repository import CRUDBase

from .models import AIHistory


class CRUDAIHistory(CRUDBase[AIHistory]):
    pass


ai_history_repo = CRUDAIHistory(AIHistory)
