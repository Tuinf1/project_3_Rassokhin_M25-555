# ruff: noqa: E501
import argparse

from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.core.usecases import (
    buy_currency,
    get_rate,
    login_user,
    logout_user,
    register_user,
    sell_currency,
    show_portfolio,
)

from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.storage import Storage
from valutatrade_hub.parser_service.api_clients import CoinGeckoClient, ExchangeRateApiClient
from valutatrade_hub.parser_service.updater import RatesUpdater


def run_update_rates(args):
    config = ParserConfig()
    storage = Storage(config)

    all_clients = {
        "coingecko": CoinGeckoClient(config),
        "exchangerate": ExchangeRateApiClient(config),
    }

    if args.source:
        clients = [all_clients[args.source]]
    else:
        clients = list(all_clients.values())

    updater = RatesUpdater(clients, storage)

    try:
        result = updater.run_update()
        if result:
            print(f"✅ Update successful. Total rates updated: {len(result['pairs'])}. Last refresh: {result['last_refresh']}")
        else:
            print("⚠️ Update failed: no rates fetched.")
    except ApiRequestError as e:
        print(f"❌ Обновление не выполнено: {e}")


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

    update_parser = subparsers.add_parser("update-rates", help="Обновить курсы валют")
    update_parser.add_argument(
        "--source",
        type=str,
        choices=["coingecko", "exchangerate"],
        help="Источник: coingecko или exchangerate. По умолчанию — оба.",
    )


    args = parser.parse_args()


    if args.command == "register":
        try:
            msg = register_user(args.username, args.password)
            print(msg)
            print(f"Войдите: login --username {args.username} --password\
                   {args.password}")
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
            print("✅ Покупка успешно выполнена!")
            print(msg)
        except CurrencyNotFoundError as e:
            print(f"❌ Ошибка: {e}")
            print("ℹ️ Поддерживаемые валюты: USD, EUR, RUB, BTC, ETH")
        except InsufficientFundsError as e:
            print(f"❌ Недостаточно средств: {e}")
            print("ℹ️ Пополните баланс или уменьшите сумму.")
        except ApiRequestError as e:
            print(f"⚠️ Ошибка обновления курса: {e}")
            print("ℹ️ Попробуйте повторить позже или проверьте подключение к сети.")
        except ValueError as e:
            print(f"❌ Некорректные данные: {e}")
        except Exception as e:
            print(f"💥 Непредвиденная ошибка: {e}")

    elif args.command == "logout":
        try:
            msg = logout_user()
            print(msg)
        except Exception as e:
            print("Ошибка:", e)

    elif args.command == "sell":
        try:
            msg = sell_currency(args.currency, args.amount)
            print("✅ Продажа успешно выполнена!")
            print(msg)
        except CurrencyNotFoundError as e:
            print(f"❌ Ошибка: {e}")
            print("ℹ️ Доступные валюты: USD, EUR, RUB, BTC, ETH")
        except InsufficientFundsError as e:
            print(f"❌ Недостаточно средств: {e}")
            print("ℹ️ Проверьте баланс с помощью команды show-portfolio.")
        except ValueError as e:
            print(f"❌ Некорректные данные: {e}")
        except Exception as e:
            print(f"💥 Непредвиденная ошибка: {e}")

    elif args.command == "get-rate":
        try:
            result = get_rate(args.from_code, args.to_code)
            print(f"Курс {args.from_code} → {args.to_code}: {result['rate']:.4f}")
            print(f"Обновлено: {result['updated_at']}")
        except CurrencyNotFoundError as e:
            print(f"[ОШИБКА: Валюта] {e}")
        except ApiRequestError as e:
            print(f"[ОШИБКА: Курс недоступен] {e}")
        except Exception as e:
            print(f"[СИСТЕМНАЯ ОШИБКА] {e}")

    elif args.command == "update-rates":
        run_update_rates(args)

if __name__ == "__main__":
    run_cli()