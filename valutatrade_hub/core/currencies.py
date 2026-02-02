# ruff: noqa: E501, RUF001
from abc import ABC, abstractmethod
from typing import Dict

from ..core.exceptions import CurrencyNotFoundError


# === БАЗОВЫЙ АБСТРАКТНЫЙ КЛАСС ===
class Currency(ABC):
    def __init__(self, code: str, name: str):
        if not isinstance(code, str) or not (2 <= len(code) <= 5) or not code.isupper() or " " in code:
            raise ValueError("Некорректный код валюты")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Название валюты не может быть пустым")

        self.code = code
        self.name = name

    @abstractmethod
    def get_display_info(self) -> str:
        pass

class FiatCurrency(Currency):
    def __init__(self, code: str, name: str, issuing_country: str):
        super().__init__(code, name)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"
    
class CryptoCurrency(Currency):
    def __init__(self, code: str, name: str, algorithm: str, market_cap: float):
        super().__init__(code, name)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"
    
_currency_registry: Dict[str, Currency] = {
    "USD": FiatCurrency("USD", "US Dollar", "United States"),
    "EUR": FiatCurrency("EUR", "Euro", "Eurozone"),
    "RUB": FiatCurrency("RUB", "Russian Ruble", "Russia"),
    "BTC": CryptoCurrency("BTC", "Bitcoin", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("ETH", "Ethereum", "Ethash", 2.35e11),
    # Добавь по необходимости
}


def get_currency(code: str) -> Currency:
    code = code.upper()
    if code not in _currency_registry:
        raise CurrencyNotFoundError(f"Валюта '{code}' не найдена")
    return _currency_registry[code]

# test
# python -m valutatrade_hub.core.currencies

# cur = get_currency("btc")
# print(cur.get_display_info())
# # → [CRYPTO] BTC — Bitcoin (Algo: SHA-256, MCAP: 1.12e+12)

# cur = get_currency("USD")
# print(cur.get_display_info())
# # → [FIAT] USD — US Dollar (Issuing: United States)