from fastapi import APIRouter

from app.contrib.chat.api import api as chat_api

api = APIRouter()

api.include_router(chat_api, tags=["chat"], prefix="/chat")
