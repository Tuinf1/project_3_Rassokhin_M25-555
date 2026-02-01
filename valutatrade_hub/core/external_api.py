import requests
from datetime import datetime
from pathlib import Path

from valutatrade_hub.core.utils import _save_json

RATES_PATH = Path("data/rates.json")


def fetch_rates() -> dict:
    """
    Загружает курсы BTC, ETH, USDT → USD
    и сохраняет их в формате {"BTC_USD": {"rate": ..., "updated_at": ...}, ...}
    """
    response = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={
            "ids": "bitcoin,ethereum,tether",
            "vs_currencies": "usd",
        },
        timeout=10
    )

    if not response.ok:
        raise RuntimeError("Ошибка при обращении к API")

    data = response.json()
    now = datetime.utcnow().isoformat()

    rates = {
        "BTC_USD": {"rate": data["bitcoin"]["usd"], "updated_at": now},
        "ETH_USD": {"rate": data["ethereum"]["usd"], "updated_at": now},
        "USDT_USD": {"rate": data["tether"]["usd"], "updated_at": now},
    }

    _save_json(RATES_PATH, rates)
    return rates