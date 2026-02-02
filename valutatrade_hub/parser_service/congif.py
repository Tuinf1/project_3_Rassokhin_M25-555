import os
from dataclasses import dataclass, field


@dataclass
class ParserConfig:
    EXCHANGERATE_API_KEY: str = field(init=False)

    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"
    BASE_CURRENCY: str = "USD"

    FIAT_CURRENCIES = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES = ("BTC", "ETH", "SOL")
    CRYPTO_ID_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    }

    RATES_FILE_PATH = "data/rates.json"
    HISTORY_FILE_PATH = "data/exchange_rates.json"
    REQUEST_TIMEOUT = 10

    def post_init(self):
        self.EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")
        if not self.EXCHANGERATE_API_KEY:
            raise RuntimeError("EXCHANGERATE_API_KEY not set in environment")