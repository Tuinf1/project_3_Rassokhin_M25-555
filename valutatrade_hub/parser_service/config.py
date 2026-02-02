import os
from dataclasses import dataclass


@dataclass
class ParserConfig:
    # EXCHANGERATE_API_KEY: str = field(init=False)
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY")
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
        
# TEST
# if __name__ == "__main__":
#     import os
#     os.environ["EXCHANGERATE_API_KEY"] = "b6007f1a62957f26dd6bfaf0"

#     config = ParserConfig()
#     print("🔑 API key:", config.EXCHANGERATE_API_KEY)
#     print("🪙 Crypto map:", config.CRYPTO_ID_MAP)
#     # print("Все поля:", dir(config))
# export EXCHANGERATE_API_KEY=b6007f1a62957f26dd6bfaf0