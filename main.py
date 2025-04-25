import sys
from datetime import datetime, timedelta
import asyncio
import platform
import aiohttp
import json

class HttpError(Exception):
    pass

async def fetch_exchange_rate(session: aiohttp.ClientSession, date: str, currencies: list[str]):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?date={date}"
    try:
        print(f"Fetching from: {url}")
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                result = extract_currency_rates(data, currencies)
                return result
            else:
                raise HttpError(f"Error status: {resp.status} for {url}")
    except (aiohttp.ClientError, aiohttp.InvalidURL) as err:
        raise HttpError(f"Connection error: {url} - {err}")

def extract_currency_rates(data, currencies):
    date = data.get("date")
    rates = {}
    for item in data.get("exchangeRate", []):
        currency = item.get("currency")
        if currency in currencies:
            rates[currency] = {
                "sale": item.get("saleRate") or item.get("saleRateNB"),
                "purchase": item.get("purchaseRate") or item.get("purchaseRateNB")
            }
    return {date: rates}


async def get_rates(days: int, currencies: list[str]):
    if not (1<= days <= 10):
        raise ValueError("Days must be between 1 and 10.")

    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(days):
            date_obj = datetime.now() - timedelta(days=i)
            formatted_date = date_obj.strftime("%d.%m.%Y")
            try:
                rate = await fetch_exchange_rate(session, formatted_date, currencies)
                results.append(rate)
            except HttpError as err:
                print(err)
    return results


async def main():
    print ("Started main func")
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print("Usage: python main.py <days 1-10> [CURRENCY1 CURRENCY2..]")
        return

    days = int(sys.argv[1])
    currencies = sys.argv[2:] or ["USD", "EUR"]
    try:
        results = await get_rates(days, currencies)
        print("Results length:", len(results))
        print("Fetched results:", results)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except ValueError as ve:
        print(f"Input error: {ve}")


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
