# valutatrade_hub/core/exceptions.py
# ruff: noqa: E501, RUF001
class CurrencyNotFoundError(Exception):
    def init(self, code: str):
        super().init(f"Неизвестная валюта '{code}'")


class InsufficientFundsError(Exception):
    def init(self, available: float, required: float, code: str):
        super().init(f"Недостаточно средств: доступно {available} {code}, требуется {required} {code}")


class ApiRequestError(Exception):
    def init(self, reason: str):
        super().init(f"Ошибка при обращении к внешнему API: {reason}")