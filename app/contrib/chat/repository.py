from app.db.repository import CRUDBase

from .models import ChatFavorite, Chat, ChatItem


class CRUDChat(CRUDBase[Chat]):
    pass


class CRUDChatItem(CRUDBase[ChatItem]):
    pass


class CRUDChatFavorite(CRUDBase[ChatFavorite]):
    pass


chat_repo = CRUDChat(Chat)
chat_item_repo = CRUDChatItem(ChatItem)
chat_favorite_repo = CRUDChatFavorite(ChatFavorite)
