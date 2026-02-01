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