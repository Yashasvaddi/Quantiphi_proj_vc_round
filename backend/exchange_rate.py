import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

BASE_URL = "https://v6.exchangerate-api.com/v6"


async def get_exchange_rate(
    from_currency: str,
    to_currency: str
):
    url = (
        f"{BASE_URL}/{API_KEY}/pair/"
        f"{from_currency}/{to_currency}"
    )

    async with httpx.AsyncClient() as client:

        response = await client.get(url)

        response.raise_for_status()

        data = response.json()

    if data.get("result") != "success":
        raise ValueError(
            f"Exchange rate API error: "
            f"{data.get('error-type', 'unknown error')}"
        )

    return data["conversion_rate"]