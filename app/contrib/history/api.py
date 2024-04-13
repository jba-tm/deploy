from typing import Optional, Literal, List
from datetime import timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text

from app.routers.dependency import get_active_user, get_async_db, get_commons
from app.core.schema import IPaginationDataBase, CommonsModel
from app.contrib.history import EntityChoices, StatisticsTypeChoices


from .repository import ai_history_repo
from .schema import AIHistoryVisible, StatisticsResult

api = APIRouter()


@api.get(
    "/", name="history-list",
    response_model=IPaginationDataBase[AIHistoryVisible]
)
async def retrieve_protocol_list(
        user=Depends(get_active_user),
        async_db=Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),
        order_by: Optional[Literal[
            "created_at", "-created_at"
        ]] = "-created_at",
):
    obj_list = await ai_history_repo.get_all(
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


@api.get('/query-count/', name='history-query-count', response_model=List[StatisticsResult])
async def history_query_count(
        user=Depends(get_active_user),
        async_db=Depends(get_async_db),
        by: StatisticsTypeChoices = Query(...),
        entity: Optional[EntityChoices] = Query(None),
):
    by_truncate = "day"
    if by == StatisticsTypeChoices.LAST_YEAR:
        by_last = "11 months"
        by_truncate = "month"
    elif by == StatisticsTypeChoices.LAST_MONTH:
        by_last = "30 days"
    else:
        by_last = "6 days"

    stmt = text(f"""
        SELECT
            COUNT(h."created_at") AS count,
            DATE_TRUNC(:by_truncate, generate_series)::date AS statistics_date
        FROM
            generate_series(NOW() - INTERVAL '{by_last}' , NOW(), INTERVAL '1 day') AS generate_series
        LEFT JOIN
            public."a_i_history" h ON DATE_TRUNC('day', h."created_at") = generate_series::date
        GROUP BY
            statistics_date
        ORDER BY
            statistics_date;
    """)

    fetch = await async_db.execute(stmt, params={"by_truncate": by_truncate})
    obj_list = fetch.fetchall()
    return obj_list
