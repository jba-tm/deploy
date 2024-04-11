from typing import Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, Query
from app.routers.dependency import get_active_user, get_async_db, get_commons
from app.core.schema import IPaginationDataBase, CommonsModel
from app.contrib.history import EntityChoices
from app.utils.datetime.timezone import today

from .models import AIHistory
from .repository import ai_history_repo


@api.get(
    "/", name="history-list",
    response_model=IPaginationDataBase[ProtocolVisible]
)
async def retrieve_protocol_list(
        user: User = Depends(get_active_user),
        async_db=Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),
        order_by: Optional[Literal[
            "created_at", "-created_at"
        ]] = "-created_at",
):
    obj_list = await protocol_repo.ai_history_repo(
        async_db=async_db,
        limit=commons.limit,
        offset=commons.offset,
        order_by=(order_by,),
    )
    if commons.with_count:
        count = await ai_history_repo.count(async_db)
    else:
        count = None
    return {
        'page': commons.page,
        'limit': commons.limit,
        "count": count,
        "rows": obj_list
    }


@api.get('/query-count/', name='history-query-count', response_model=int)
async def history_query_count(
        user: User = Depends(get_active_user),
        async_db=Depends(get_async_db),
        last_days: Optional[int] = Query(None),
        entity: Optional[EntityChoices] = Query(None)
):
    expressions = []
    if last_days:
        from_datetime = today() - timedelta(days=last_days)
        expressions.append(AIHistory.created_at>from_datetime)
    if entity:
        expressions.append(AIHistory.entity == entity)
    return await ai_history_repo.count(async_db, expressions=expressions)
