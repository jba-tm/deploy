import pytest
from typing import TYPE_CHECKING
from app.conf.config import settings
if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gk_clinic_trials_generation_api(
        async_client: "AsyncClient",
        simple_user_token_headers: dict,
) -> None:
    data = {
        "search": "NCT06106880",
        "filters": []
    }
    response = await async_client.post(
        f'{settings.API_V1_STR}/gk/generate/clinical-trials/',
        json=data,
        headers=simple_user_token_headers,
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_gk_medicine_generation_api(
        async_client: "AsyncClient",
        simple_user_token_headers: dict,
) -> None:
    data = {
        "search": "Lepirudin",
        "filters": []
    }

    response = await async_client.post(
        f'{settings.API_V1_STR}/gk/generate/medicine/',
        json=data,
        headers=simple_user_token_headers,
    )

