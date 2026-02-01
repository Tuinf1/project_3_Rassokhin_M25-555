import json
import hashlib
import secrets
from datetime import datetime
from pathlib import Path

USERS_PATH = Path("data/users.json")
PORTFOLIOS_PATH = Path("data/portfolios.json")


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
    portfolios.append({
        "user_id": user_id,
        "wallets": {}
    })
    _save_json(PORTFOLIOS_PATH, portfolios)

    return f"Пользователь '{username}' зарегистрирован (id={user_id})."


# login

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
    if not portfolio or not portfolio.get("wallets"):
        return f"Портфель пользователя '{username}' пуст."

    wallets = portfolio["wallets"]

    # Получаем курсы
    rates_data = _load_json(Path("data/rates.json"))

    # Проверка, что base существует
    if base_currency.upper() not in ["USD", "BTC", "EUR", "ETH", "RUB"]:
        raise ValueError(f"Неизвестная базовая валюта '{base_currency}'")

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