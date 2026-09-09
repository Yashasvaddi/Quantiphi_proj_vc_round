import httpx

FRANKFURTER_URL = "https://api.frankfurter.dev/v2/rates"


async def get_historical_rates(
    from_currency: str,
    to_currency: str,
    start_date: str,
    end_date: str
):
    params = {
        "base": from_currency,
        "quotes": to_currency,
        "from": start_date,
        "to": end_date
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            FRANKFURTER_URL,
            params=params
        )

        response.raise_for_status()

        return response.json()