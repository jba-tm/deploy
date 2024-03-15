from app.db.repository import CRUDBase

from .models import ChatFavorite, ChatHistory


class CRUDChatHistory(CRUDBase[ChatHistory]):
    pass


class CRUDChatFavorite(CRUDBase[ChatFavorite]):
    pass


chat_history_repo = CRUDChatHistory(ChatHistory)
chat_favorite_repo = CRUDChatFavorite(ChatFavorite)
