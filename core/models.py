import hashlib
import secrets
from datetime import datetime

class User:
    def init(
        self,
        user_id: int,
        username: str,
        password: str,
        registration_date: datetime
    ):
        self.__user_id = user_id
        self.username = username          # через сеттер
        self.__salt = self.__generate_salt()
        self.__hashed_password = self.__hash_password(password, self.__salt)
        self.__registration_date = registration_date

    # =========================
    # ВНУТРЕННИЕ МЕТОДЫ
    # =========================

    def __generate_salt(self) -> str:
        return secrets.token_hex(8)

    def __hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256(
            (password + salt).encode("utf-8")
        ).hexdigest()

    # =========================
    # GETTERS / SETTERS
    # =========================

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def username(self) -> str:
        return self.__username

    @username.setter
    def username(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Имя пользователя не может быть пустым.")
        self.__username = value

    @property
    def registration_date(self) -> datetime:
        return self.__registration_date

    # =========================
    # ОСНОВНЫЕ МЕТОДЫ
    # =========================

    def get_user_info(self) -> dict:
        return {
            "user_id": self.__user_id,
            "username": self.__username,
            "registration_date": self.__registration_date.isoformat()
        }

    def change_password(self, new_password: str) -> None:
        if not isinstance(new_password, str) or len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")

        self.__salt = self.__generate_salt()
        self.__hashed_password = self.__hash_password(new_password, self.__salt)

    def verify_password(self, password: str) -> bool:
        return (
            self.__hashed_password
            == self.__hash_password(password, self.__salt)
        )

    # =========================
    # ДЛЯ JSON-СЕРИАЛИЗАЦИИ
    # =========================

    def to_dict(self) -> dict:
        return {
            "user_id": self.__user_id,
            "username": self.__username,
            "hashed_password": self.__hashed_password,
            "salt": self.__salt,
            "registration_date": self.__registration_date.isoformat()
        }


class Wallet:
    def init(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self.balance = balance  # через сеттер

    # =========================
    # ГЕТТЕР/СЕТТЕР BALANCE
    # =========================

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Баланс должен быть числом.")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным.")
        self._balance = float(value)

    # =========================
    # ОСНОВНЫЕ МЕТОДЫ
    # =========================

    def deposit(self, amount: float) -> None:
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительным числом.")
        self._balance += float(amount)

    def withdraw(self, amount: float) -> None:
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Сумма снятия должна быть положительным числом.")
        if amount > self._balance:
            raise ValueError("Недостаточно средств на балансе.")
        self._balance -= float(amount)

    def get_balance_info(self) -> dict:
        return {
            "currency_code": self.currency_code,
            "balance": round(self._balance, 2)
        }