import argparse
from valutatrade_hub.core.usecases import register_user, login_user, show_portfolio, buy_currency, logout_user, sell_currency, get_exchange_rate
from valutatrade_hub.core.settings import SettingsLoader

from valutatrade_hub.core.exceptions import (
    CurrencyNotFoundError,
    InsufficientFundsError,
    ApiRequestError
)

def run_cli():
    parser = argparse.ArgumentParser(description="Crypto CLI")
    subparsers = parser.add_subparsers(dest="command")

    # === REGISTER ===
    register_parser = subparsers.add_parser("register", help="Зарегистрировать нового пользователя")
    register_parser.add_argument("--username", required=True, help="Имя пользователя")
    register_parser.add_argument("--password", required=True, help="Пароль (минимум 4 символа)")

        # === LOGIN ===
    login_parser = subparsers.add_parser("login", help="Войти в систему")
    login_parser.add_argument("--username", required=True, help="Имя пользователя")
    login_parser.add_argument("--password", required=True, help="Пароль")

    # === LOGOUT ===
    subparsers.add_parser("logout", help="Выйти из системы")

    # === SHOW-PORTFOLIO ===
    portfolio_parser = subparsers.add_parser("show-portfolio", help="Показать портфель пользователя")
    portfolio_parser.add_argument("--base", default="USD", help="Базовая валюта (по умолчанию USD)")

    # === SELL ===
    sell_parser = subparsers.add_parser("sell", help="Продать валюту")
    sell_parser.add_argument("--currency", required=True, help="Код валюты (например BTC)")
    sell_parser.add_argument("--amount", required=True, type=float, help="Сколько продать")
    # ===

        # === GET-RATE ===
    rate_parser = subparsers.add_parser("get-rate", help="Получить курс валюты")
    rate_parser.add_argument("--from", dest="from_currency", required=True, help="Исходная валюта")
    rate_parser.add_argument("--to", dest="to_currency", required=True, help="Целевая валюта")
    
    # === BUY ===
    buy_parser = subparsers.add_parser("buy", help="Купить валюту")
    buy_parser.add_argument("--currency", required=True, help="Код валюты (например BTC)")
    buy_parser.add_argument("--amount", required=True, type=float, help="Сколько купить")

    args = parser.parse_args()


    if args.command == "register":
        try:
            msg = register_user(args.username, args.password)
            print(msg)
            print(f"Войдите: login --username {args.username} --password {args.password}")
        except ValueError as e:
            print("Ошибка:", e)

    elif args.command == "login":
        try:
            msg = login_user(args.username, args.password)
            print(msg)
        except ValueError as e:
            print("Ошибка:", e)

    elif args.command == "show-portfolio":
        try:
            msg = show_portfolio(args.base)
            print(msg)
        except CurrencyNotFoundError as e:
            print(f"❌ {e}")
            print("Поддерживаемые валюты: USD, EUR, RUB, BTC, ETH")
        except ValueError as e:
            print("Ошибка:", e)

    elif args.command == "buy":
        try:
            msg = buy_currency(args.currency, args.amount)
            print(msg)
        except CurrencyNotFoundError as e:
            print(f"❌ {e}")
            print("Поддерживаемые валюты: USD, EUR, RUB, BTC, ETH")
        except InsufficientFundsError as e:
            print(f"❌ {e}")
        except ApiRequestError as e:
            print(f"⚠️ {e}")
            print("Попробуйте повторить позже или проверьте подключение к сети.")
        except ValueError as e:
            print("Ошибка:", e)

    elif args.command == "logout":
        try:
            msg = logout_user()
            print(msg)
        except Exception as e:
            print("Ошибка:", e)

    elif args.command == "sell":
        try:
            msg = sell_currency(args.currency, args.amount)
            print(msg)
        except CurrencyNotFoundError as e:
            print(f"❌ {e}")
            print("Поддерживаемые валюты: USD, EUR, RUB, BTC, ETH")
        except InsufficientFundsError as e:
            print(f"❌ {e}")
        except ValueError as e:
            print("Ошибка:", e)

    elif args.command == "get-rate":
        try:
            msg = get_exchange_rate(args.from_currency, args.to_currency)
            print(msg)
        except CurrencyNotFoundError as e:
            print(f"❌ {e}")
            print("Поддерживаемые валюты: USD, EUR, RUB, BTC, ETH")
        except ApiRequestError as e:
            print(f"⚠️ {e}")
            print("Попробуйте повторить позже или проверьте подключение к сети.")
        except ValueError as e:
            print("Ошибка:", e)



if __name__ == "__main__":
    run_cli()