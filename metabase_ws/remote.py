from urllib.parse import urljoin

import httpx
from sanic.log import logger


async def FetchQSales(
    overlord_host: str, overlord_username: str, overlord_password: str
):
    async with httpx.AsyncClient(verify=False) as client:
        api_key = await _FetchApiKey(
            client, overlord_host, overlord_username, overlord_password
        )

        url = urljoin(overlord_host, "api/v1/metrics/q-sales/")
        response = await client.get(
            url,
            params={"start_date": "2023-01-01", "end_date": "2025-05-01"},
            headers={
                "Authorization": f"Api-Key {api_key}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code != 200:
            logger.error(
                f"Failed to fetch QSale data: {response.status_code} - {response.text}"
            )
            raise ValueError("Failed to fetch QSale data")

        return response.json()


async def _FetchApiKey(
    client, overlord_host, overlord_username, overlord_password
):
    url = urljoin(overlord_host, "api/v1/auth/signin/")
    response = await client.post(
        url,
        json={
            "username": overlord_username,
            "password": overlord_password,
        },
    )

    if response.status_code != 200:
        logger.error(
            f"Failed to authenticate: {response.status_code} - {response.text}"
        )
        raise ValueError("Failed to authenticate")

    api_key = response.json().get("api_key")
    if not api_key:
        logger.error(
            f"Failed to fetch API key: {response.status_code} - {response.text}"
        )
        raise ValueError("Failed to fetch API key")

    return api_key
