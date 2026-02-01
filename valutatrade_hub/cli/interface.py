import argparse
from valutatrade_hub.core.usecases import register_user


def run_cli():
    parser = argparse.ArgumentParser(description="Crypto CLI")
    subparsers = parser.add_subparsers(dest="command")

    # === REGISTER ===
    register_parser = subparsers.add_parser("register", help="Зарегистрировать нового пользователя")
    register_parser.add_argument("--username", required=True, help="Имя пользователя")
    register_parser.add_argument("--password", required=True, help="Пароль (минимум 4 символа)")

    args = parser.parse_args()

    if args.command == "register":
        try:
            msg = register_user(args.username, args.password)
            print(msg)
            print(f"Войдите: login --username {args.username} --password {args.password}")
        except ValueError as e:
            print("Ошибка:", e)


if __name__ == "__main__":
    run_cli()