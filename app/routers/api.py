from fastapi import APIRouter

from app.contrib.account.api import api as account_api
from app.contrib.chat.api import api as chat_api
from app.contrib.protocol.api import api as protocol_api
api = APIRouter()


api.include_router(account_api, tags=["account"])
api.include_router(chat_api, tags=["chat"], prefix="/chat")
api.include_router(protocol_api, tags=["chat"], prefix="/protocol")
