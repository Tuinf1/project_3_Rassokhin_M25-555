# ruff: noqa: E501, RUF001
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import ApiRequestError, CurrencyNotFoundError
from valutatrade_hub.core.external_api import fetch_rates
from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.decorators import log_action

RATES_PATH = Path("data/rates.json")
USERS_PATH = Path("data/users.json")
PORTFOLIOS_PATH = Path("data/portfolios.json")


def get_rate(from_code: str, to_code: str) -> dict:
    # Валидация кодов валют
    try:
        from_currency = get_currency(from_code)
        to_currency = get_currency(to_code)
    except ValueError:
        raise CurrencyNotFoundError(f"Валюта '{from_code}' или '{to_code}' не найдена")

    # Получаем TTL из настроек
    settings = SettingsLoader.load()
    ttl_seconds = settings.get("rates_ttl", 3600)  # по умолчанию 1 час

    # Чтение кэша
    rates = _load_json(RATES_PATH)

    rate_key = f"{from_currency.code}_{to_currency.code}"
    inverse_key = f"{to_currency.code}_{from_currency.code}"

    now = datetime.utcnow()

    # Проверка актуальности по ключу
    def is_fresh(rate_data: dict) -> bool:
        updated_at = datetime.fromisoformat(rate_data["updated_at"])
        return now - updated_at <= timedelta(seconds=ttl_seconds)

    if rate_key in rates and is_fresh(rates[rate_key]):
        return {
            "rate": rates[rate_key]["rate"],
            "updated_at": rates[rate_key]["updated_at"],
        }

    if inverse_key in rates and is_fresh(rates[inverse_key]):
        rate = 1 / rates[inverse_key]["rate"]
        return {
            "rate": rate,
            "updated_at": rates[inverse_key]["updated_at"],
        }

    # Если нет или устарело — обновляем
    try:
        new_rates = fetch_rates()  # функция загружает и сохраняет rates.json
        rates.update(new_rates)
        _save_json(RATES_PATH, rates)
    except Exception as e:
        raise ApiRequestError(f"Не удалось обновить курсы: {e}")

    # Повторяем проверку
    if rate_key in rates:
        return {
            "rate": rates[rate_key]["rate"],
            "updated_at": rates[rate_key]["updated_at"],
        }

    if inverse_key in rates:
        rate = 1 / rates[inverse_key]["rate"]
        return {
            "rate": rate,
            "updated_at": rates[inverse_key]["updated_at"],
        }

    raise ValueError(f"Нет данных курса между {from_code} и {to_code}")




def _load_json(path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _save_json(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@log_action("REGISTER")
def register_user(username: str, password: str) -> str:
    # 1. Проверка username
    if not username.strip():
        raise ValueError("Имя пользователя не может быть пустым.")

    if len(password) < 4:
        raise ValueError("Пароль должен быть не короче 4 символов.")

    users = _load_json(USERS_PATH)

    if any(user["username"] == username for user in users):
        raise ValueError(f"Имя пользователя '{username}' уже занято")

    # 2. Генерация user_id
    user_id = max((u["user_id"] for u in users), default=0) + 1

    # 3. Хеширование пароля
    salt = secrets.token_hex(8)
    hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    # 4. Сохранение в users.json
    user_obj = {
        "user_id": user_id,
        "username": username,
        "hashed_password": hashed,
        "salt": salt,
        "registration_date": datetime.now().isoformat()
    }

    users.append(user_obj)
    _save_json(USERS_PATH, users)

    # 5. Создание пустого портфеля
    portfolios = _load_json(PORTFOLIOS_PATH)
    existing = any(p["user_id"] == user_id for p in portfolios)

    if not existing:
        portfolios.append({
            "user_id": user_id,
            "wallets": {}
        })
        _save_json(PORTFOLIOS_PATH, portfolios)

    return f"Пользователь '{username}' зарегистрирован (id={user_id})."


# login
@log_action("LOGIN")
def login_user(username: str, password: str) -> str:
    users = _load_json(USERS_PATH)

    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise ValueError(f"Пользователь '{username}' не найден")

    salt = user["salt"]
    expected_hash = user["hashed_password"]
    actual_hash = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    if actual_hash != expected_hash:
        raise ValueError("Неверный пароль")

    # Сохраняем user_id в session.json
    session_path = Path("data/session.json")
    session = {"user_id": user["user_id"]}
    _save_json(session_path, session)

    return f"Вы вошли как '{username}'"


def logout_user() -> str:
    session_path = Path("data/session.json")
    if session_path.exists():
        session_path.unlink()  # удалить файл
    return "Вы вышли из системы."


def show_portfolio(base_currency: str = "USD") -> str:
    session = _load_json(Path("data/session.json"))
    if not session or "user_id" not in session:
        raise ValueError("Сначала выполните login")

    user_id = session["user_id"]

    # Получаем имя пользователя
    users = _load_json(USERS_PATH)
    user = next((u for u in users if u["user_id"] == user_id), None)
    if not user:
        raise ValueError("Пользователь не найден")

    username = user["username"]

    # Получаем портфель
    portfolios = _load_json(PORTFOLIOS_PATH)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)

    # Проверка, что base существует
    if base_currency.upper() not in ["USD", "BTC", "EUR", "ETH", "RUB"]:
        raise ValueError(f"Неизвестная базовая валюта '{base_currency}'")

    if not portfolio or not portfolio.get("wallets"):
        return f"Портфель пользователя '{username}' пуст."

    wallets = portfolio["wallets"]

    # Получаем курсы
    rates_data = _load_json(Path("data/rates.json"))

    
    total = 0.0
    output = [f"Портфель пользователя '{username}' (база: {base_currency.upper()}):"]

    for code, wallet in wallets.items():
        balance = wallet["balance"]
        from_cur = code.upper()
        to_cur = base_currency.upper()

        if from_cur == to_cur:
            converted = balance
        else:
            rate_key = f"{from_cur}_{to_cur}"
            inverse_key = f"{to_cur}_{from_cur}"

            if rate_key in rates_data:
                rate = rates_data[rate_key]["rate"]
                converted = balance * rate
            elif inverse_key in rates_data:
                rate = rates_data[inverse_key]["rate"]
                converted = balance / rate
            else:
                raise ValueError(f"Нет курса для {from_cur} -> {to_cur}")

        total += converted
        output.append(f"- {from_cur}: {balance:.2f} → {converted:.2f} {to_cur}")

    output.append(f"\nИТОГО: {total:.2f} {base_currency.upper()}")
    return "\n".join(output)

@log_action("BUY")
def buy_currency(currency: str, amount: float) -> str:
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("'amount' должен быть положительным числом.")

    # Валидация валюты через get_currency()
    currency_obj = get_currency(currency)
    currency_code = currency_obj.code

    # Шаг 1. Проверка логина
    session = _load_json(Path("data/session.json"))
    if not session or "user_id" not in session:
        raise ValueError("Сначала выполните login")

    user_id = session["user_id"]

    # Шаг 2. Получаем пользователя
    users = _load_json(USERS_PATH)
    user = next((u for u in users if u["user_id"] == user_id), None)
    if not user:
        raise ValueError("Пользователь не найден")
    # username = user["username"]

    # Шаг 3. Загружаем портфель
    portfolios = _load_json(PORTFOLIOS_PATH)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio:
        raise ValueError("Портфель пользователя не найден")

    wallets = portfolio.setdefault("wallets", {})

    # Шаг 4. Если нет кошелька — создаём
    if currency_code not in wallets:
        wallets[currency_code] = {
            "currency_code": currency_code,
            "balance": 0.0
        }

    before = wallets[currency_code]["balance"]
    wallets[currency_code]["balance"] += amount
    after = wallets[currency_code]["balance"]

    # Шаг 5. Загружаем курс для расчёта стоимости в USD
    rates = _load_json(Path("data/rates.json"))
    rate_key = f"{currency_code}_USD"
    inverse_key = f"USD_{currency_code}"

    if rate_key in rates:
        rate = rates[rate_key]["rate"]
        total_usd = amount * rate
        rate_info = f"{rate:.2f} USD/{currency_code}"
    elif inverse_key in rates:
        rate = rates[inverse_key]["rate"]
        total_usd = amount / rate
        rate_info = f"1/{rate:.4f} USD/{currency_code}"
    else:
        raise ValueError(f"Не удалось получить курс {currency_code} → USD")

    # Шаг 6. Сохраняем изменения
    _save_json(PORTFOLIOS_PATH, portfolios)

    return (
        f"Покупка выполнена: {amount:.4f} {currency_code} по курсу {rate_info}\n"
        f"Изменения в портфеле:\n"
        f"- {currency_code}: было {before:.4f} → стало {after:.4f}\n"
        f"Оценочная стоимость покупки: {total_usd:.2f} USD"
    )

@log_action("SELL")
def sell_currency(currency: str, amount: float) -> str:
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("'amount' должен быть положительным числом.")

    # Валидация валюты через get_currency()
    currency_obj = get_currency(currency)
    currency_code = currency_obj.code

    # Проверка логина
    session = _load_json(Path("data/session.json"))
    if not session or "user_id" not in session:
        raise ValueError("Сначала выполните login")
    user_id = session["user_id"]

    # Загрузка пользователя
    users = _load_json(USERS_PATH)
    user = next((u for u in users if u["user_id"] == user_id), None)
    if not user:
        raise ValueError("Пользователь не найден")
    # username = user["username"]

    # Загрузка портфеля
    portfolios = _load_json(PORTFOLIOS_PATH)
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if not portfolio:
        raise ValueError("Портфель пользователя не найден")

    wallets = portfolio.get("wallets", {})

    # Проверка кошелька и средств
    if currency_code not in wallets:
        raise ValueError(f"У вас нет кошелька '{currency_code}'.")

    balance = wallets[currency_code]["balance"]
    if balance < amount:
        raise ValueError(
            f"Недостаточно средств: доступно {balance:.4f} {currency_code}, требуется {amount:.4f} {currency_code}"
        )

    # Получаем курс для расчёта выручки в USD
    rates = _load_json(Path("data/rates.json"))
    rate_key = f"{currency_code}_USD"
    inverse_key = f"USD_{currency_code}"

    if rate_key in rates:
        rate = rates[rate_key]["rate"]
        usd_amount = amount * rate
        rate_info = f"{rate:.2f} USD/{currency_code}"
    elif inverse_key in rates:
        rate = rates[inverse_key]["rate"]
        usd_amount = amount / rate
        rate_info = f"1/{rate:.4f} USD/{currency_code}"
    else:
        raise ValueError(f"Не удалось получить курс {currency_code} → USD")

    # Списание валюты
    before = wallets[currency_code]["balance"]
    wallets[currency_code]["balance"] -= amount
    after = wallets[currency_code]["balance"]

    # Зачисление в USD
    if "USD" not in wallets:
        wallets["USD"] = {"currency_code": "USD", "balance": 0.0}
    wallets["USD"]["balance"] += usd_amount

    _save_json(PORTFOLIOS_PATH, portfolios)

    return (
        f"Продажа выполнена: {amount:.4f} {currency_code} по курсу {rate_info}\n"
        f"Изменения в портфеле:\n"
        f"- {currency_code}: было {before:.4f} → стало {after:.4f}\n"
        f"Оценочная выручка: {usd_amount:.2f} USD"
    )
# @log_action("SELL")
# def sell_currency(currency: str, amount: float) -> str:
#     if not isinstance(amount, (int, float)) or amount <= 0:
#         raise ValueError("'amount' должен быть положительным числом.")

#     currency = currency.upper()

#     session = _load_json(Path("data/session.json"))
#     if not session or "user_id" not in session:
#         raise ValueError("Сначала выполните login")
#     user_id = session["user_id"]

#     users = _load_json(USERS_PATH)
#     user = next((u for u in users if u["user_id"] == user_id), None)
#     if not user:
#         raise ValueError("Пользователь не найден")
#     username = user["username"]

#     portfolios = _load_json(PORTFOLIOS_PATH)
#     portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
#     if not portfolio:
#         raise ValueError("Портфель пользователя не найден")

#     wallets = portfolio["wallets"]

#     # Проверка: есть ли валюта
#     if currency not in wallets:
#         raise ValueError(f"У вас нет кошелька '{currency}'.")

#     balance = wallets[currency]["balance"]
#     if balance < amount:
#         raise ValueError(
#             f"Недостаточно средств: доступно {balance:.4f} {currency}, требуется {amount:.4f} {currency}"
#         )

#     # Получаем курс
#     rates = _load_json(Path("data/rates.json"))
#     rate_key = f"{currency}_USD"
#     inverse_key = f"USD_{currency}"

#     if rate_key in rates:
#         rate = rates[rate_key]["rate"]
#         usd_amount = amount * rate
#         rate_info = f"{rate:.2f} USD/{currency}"
#     elif inverse_key in rates:
#         rate = rates[inverse_key]["rate"]
#         usd_amount = amount / rate
#         rate_info = f"1/{rate:.4f} USD/{currency}"
#     else:
#         raise ValueError(f"Не удалось получить курс для {currency} → USD")

#     # Списание валюты
#     before = wallets[currency]["balance"]
#     wallets[currency]["balance"] -= amount
#     after = wallets[currency]["balance"]

#     # Зачисление в USD
#     if "USD" not in wallets:
#         wallets["USD"] = {"currency_code": "USD", "balance": 0.0}
#     wallets["USD"]["balance"] += usd_amount

#     _save_json(PORTFOLIOS_PATH, portfolios)

#     return (
#         f"Продажа выполнена: {amount:.4f} {currency} по курсу {rate_info}\n"
#         f"Изменения в портфеле:\n"
#         f"- {currency}: было {before:.4f} → стало {after:.4f}\n"
#         f"Оценочная выручка: {usd_amount:.2f} USD"
#     )



def get_exchange_rate(from_cur: str, to_cur: str) -> str:

    ttl = SettingsLoader().get("rates_ttl_seconds", 3600)
    # path = SettingsLoader().get("data_path", "data/")

    

    from_cur = from_cur.upper()
    to_cur = to_cur.upper()

    if not from_cur or not to_cur:
        raise ValueError("Коды валют не должны быть пустыми")

    key = f"{from_cur}_{to_cur}"
    inverse_key = f"{to_cur}_{from_cur}"

    rates_path = Path("data/rates.json")
    rates = _load_json(rates_path)

    # Курс прямой
    if key in rates:
        rate_info = rates[key]
        rate = rate_info["rate"]

        updated_at = datetime.fromisoformat(rate_info["updated_at"])
        if datetime.now() - updated_at > timedelta(seconds=ttl):
            raise ValueError("Курс устарел, обновите данные")

        # age = datetime.now() - updated_at
        formatted_time = updated_at.strftime("%Y-%m-%d %H:%M:%S")

        response = f"Курс {key}: {rate:.8f} (обновлено: {formatted_time})"

        # Обратный (если есть)
        if inverse_key in rates:
            inv_rate = rates[inverse_key]["rate"]
            response += f"\nОбратный курс {inverse_key}: {inv_rate:.2f}"
        return response

    # Попробовать найти обратный
    if inverse_key in rates:
        rate_info = rates[inverse_key]
        rate = 1 / rate_info["rate"]
        updated_at = datetime.fromisoformat(rate_info["updated_at"])
        formatted_time = updated_at.strftime("%Y-%m-%d %H:%M:%S")

        response = f"Курс {key}: {rate:.8f} (обратный из {inverse_key}, обновлено: {formatted_time})"
        response += f"\nОбратный курс {inverse_key}: {rate_info['rate']:.2f}"
        return response

    raise ValueError(f"Курс {key} недоступен. Повторите попытку позже.")

# test 3.3S
# if __name__ == "__main__":
#     from valutatrade_hub.core.settings import SettingsLoader

#     settings = SettingsLoader()
#     print("DATA_PATH =", settings.get("data_path"))
#     print("TTL =", settings.get("rates_ttl_seconds"))
#     print("BASE =", settings.get("default_base_currency"))
#     print("LOG =", settings.get("log_path"))