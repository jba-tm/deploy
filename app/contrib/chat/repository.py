from app.db.repository import CRUDBase

from .models import ChatFavorite, Chat, ChatItem, ChatItemBody, ChatItemAnswer


class CRUDChatItemAnswer(CRUDBase[ChatItemAnswer]):
    pass

class CRUDChatItemBody(CRUDBase[ChatItemBody]):
    pass

class CRUDChat(CRUDBase[Chat]):
    pass


class CRUDChatItem(CRUDBase[ChatItem]):
    pass


class CRUDChatFavorite(CRUDBase[ChatFavorite]):
    pass


chat_repo = CRUDChat(Chat)
chat_item_repo = CRUDChatItem(ChatItem)
chat_item_body_repo = CRUDChatItemBody(ChatItemBody)
chat_item_answer_repo = CRUDChatItemAnswer(ChatItemAnswer)
chat_favorite_repo = CRUDChatFavorite(ChatFavorite)
