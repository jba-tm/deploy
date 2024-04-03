from fastapi import APIRouter, Depends

from app.routers.dependency import get_active_user
from app.contrib.account.models import User

api = APIRouter()


@api.post('/generate/', name="gk-generate", response_model=str)
async def generate_graph_knowledge(
        user: User = Depends(get_active_user),
):
    return ""
