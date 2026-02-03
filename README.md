source venv/bin/activate



finalproject_<фамилия>_<группа>/
│  
├── data/
│    ├── users.json             # список пользователей
│    ├── portfolios.json        # портфели и кошельки
│    └── rates.json             # курсы валют
├── valutatrade_hub/
│    ├── __init__.py
│    ├── core/
│    │    ├── __init__.py
│    │    ├── models.py         # реализация классов  
│    │    ├── utils.py          # вспомогательные функции
│    │    └── usecases.py       # бизнес-логика 
│    └── cli/
│         ├─ __init__.py
│         └─ interface.py       # команды
│
├── main.py
├── Makefile
├── poetry.lock
├── pyproject.toml
├── README.md
└── .gitignore                 # исключить dist/, pycache/ и т.п.

Запись:

https://asciinema.org/a/TqUXXlOUAMgK5dl9

Запись демонстрации get-rate и show-rates:

[show-rates](https://asciinema.org/a/IfaqZuHUKSCF0wSb)


python -m valutatrade_hub.cli.interface register --username alice --password 1234

python -m valutatrade_hub.cli.interface login --username alice --password 1234

python -m valutatrade_hub.cli.interface show-portfolio --base usd

python -m valutatrade_hub.cli.interface buy --currency BTC --amount 0.05

python -m valutatrade_hub.cli.interface sell --currency BTC --amount 0.01

python -m valutatrade_hub.cli.interface get-rate --from USD --to BTC


test api udates-rates:
python -m valutatrade_hub.cli.interface update-rates





📋 Список CLI-команд valutatrade_hub
Команда  Описание
register  Регистрация нового пользователя
💡 Аргументы: --username, --password
login  Авторизация пользователя
💡 Аргументы: --username, --password
logout  Выход из системы (завершение сессии)
show-portfolio  Показывает все кошельки и их стоимость в базовой валюте
💡 --base USD
buy  Покупка указанной валюты по текущему курсу
💡 --currency, --amount
sell  Продажа валюты из кошелька
💡 --currency, --amount
get-rate  Получить актуальный курс между двумя валютами
💡 --from, --to

💱 Поддерживаемые валюты: USD, EUR, RUB, BTC, ETH