import requests
from abc import ABC, abstractmethod
from datetime import datetime
from valutatrade_hub.core.exceptions import ApiRequestError


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self) -> dict:
        """Возвращает словарь вида {'BTC_USD': {'rate': ..., 'timestamp': ..., 'source': ...}}"""
        pass


class CoinGeckoClient(BaseApiClient):
    def __init__(self, config):
        self.config = config

    def fetch_rates(self) -> dict:
        ids = ",".join(self.config.CRYPTO_ID_MAP.values())

        params = {"ids": ids, "vs_currencies": self.config.BASE_CURRENCY.lower()}
        
        try:
            resp = requests.get(
                self.config.COINGECKO_URL,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"CoinGecko network error: {e}")

        if resp.status_code != 200:
            raise ApiRequestError(f"Bad response from CoinGecko: {resp.status_code}")

        data = resp.json()
        timestamp = datetime.utcnow().isoformat() + "Z"

        result = {}
        for symbol, coin_id in self.config.CRYPTO_ID_MAP.items():
            value = data.get(coin_id, {}).get(self.config.BASE_CURRENCY.lower())
            if value is None:
                continue

            pair = f"{symbol}_{self.config.BASE_CURRENCY}"

            result[pair] = {
                "from_currency": symbol,
                "to_currency": self.config.BASE_CURRENCY,
                "rate": value,
                "timestamp": timestamp,
                "source": "CoinGecko",
                "meta": {"raw_id": coin_id, "status_code": resp.status_code},
            }

        return result


class ExchangeRateApiClient(BaseApiClient):
    def __init__(self, config):
        self.config = config

    def fetch_rates(self) -> dict:
        if not self.config.EXCHANGERATE_API_KEY:
            raise ApiRequestError("EXCHANGERATE_API_KEY is not set")

        url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"

        try:
            resp = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"ExchangeRate-API network error: {e}")

        if resp.status_code != 200:
            raise ApiRequestError(f"Bad response from ExchangeRate-API: {resp.status_code}")

        data = resp.json()

        timestamp = data.get("time_last_update_utc") or datetime.utcnow().isoformat() + "Z"
        rates = data.get("rates", {})

        result = {}

        for cur in self.config.FIAT_CURRENCIES:
            if cur not in rates:
                continue

            pair = f"{cur}_{self.config.BASE_CURRENCY}"

            result[pair] = {
                "from_currency": cur,
                "to_currency": self.config.BASE_CURRENCY,
                "rate": rates[cur],
                "timestamp": timestamp,
                "source": "ExchangeRate-API",
                "meta": {"status_code": resp.status_code},
            }

        return result

    # test     
    
    # if __name__ == "__main__":
    #     from config import ParserConfig
    #     config = ParserConfig()
    #     client = CoinGeckoClient(config)
    #     rates = client.fetch_rates()
    #     for k, v in rates.items():
    #         print(k, v)