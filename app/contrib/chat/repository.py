from app.db.repository import CRUDBase

from .models import Chat, ChatItem, ChatItemBody, ChatItemAnswer


class CRUDChatItemAnswer(CRUDBase[ChatItemAnswer]):
    pass


class CRUDChatItemBody(CRUDBase[ChatItemBody]):
    pass


class CRUDChat(CRUDBase[Chat]):
    pass


class CRUDChatItem(CRUDBase[ChatItem]):
    pass


chat_repo = CRUDChat(Chat)
chat_item_repo = CRUDChatItem(ChatItem)
chat_item_body_repo = CRUDChatItemBody(ChatItemBody)
chat_item_answer_repo = CRUDChatItemAnswer(ChatItemAnswer)
