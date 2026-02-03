source venv/bin/activate

# ValutaTrade Hub

CLI-приложение для управления пользователями, валютными курсами и портфелями.
---

## Возможности

- Регистрация и авторизация пользователей
- Хранение портфелей и балансов валют
- Покупка и продажа валют
- Получение текущих курсов
- Обработка ошибок (недостаточно средств, неизвестная валюта)
- Демонстрация работы через CLI


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



📌 CLI-команды valutatrade_hub

Запуск всех команд:

python -m valutatrade_hub.cli.interface <command> [options]

🔐 register — регистрация нового пользователя

Создаёт нового пользователя и инициализирует пустой портфель.

Аргументы (обязательные):

--username <str> — имя пользователя

--password <str> — пароль (минимум 4 символа)

Пример:

python -m valutatrade_hub.cli.interface register \
  --username alice \
  --password 1234

🔑 login — вход в систему

Авторизует пользователя и сохраняет сессию (data/session.json).

Аргументы (обязательные):

--username <str>

--password <str>

Пример:

python -m valutatrade_hub.cli.interface login \
  --username alice \
  --password 1234

🚪 logout — выход из системы

Завершает текущую сессию (удаляет session.json).

Аргументы: отсутствуют

Пример:

python -m valutatrade_hub.cli.interface logout

💼 show-portfolio — просмотр портфеля пользователя

Показывает все кошельки и их стоимость в базовой валюте.

Аргументы (опционально):

--base <str> — базовая валюта (по умолчанию USD)

Пример:

python -m valutatrade_hub.cli.interface show-portfolio
python -m valutatrade_hub.cli.interface show-portfolio --base USD

💰 buy — покупка валюты

Покупка указанной валюты по текущему курсу из локального кеша.

Аргументы (обязательные):

--currency <str> — код валюты (например BTC)

--amount <float> — количество для покупки

Пример:

python -m valutatrade_hub.cli.interface buy \
  --currency BTC \
  --amount 0.01

💸 sell — продажа валюты

Продажа валюты из кошелька с расчётом выручки в USD.

Аргументы (обязательные):

--currency <str> — код валюты

--amount <float> — количество для продажи

Пример:

python -m valutatrade_hub.cli.interface sell \
  --currency BTC \
  --amount 0.005

📈 get-rate — получить курс между двумя валютами

Возвращает актуальный курс из локального кеша с учётом TTL.

Аргументы (обязательные):

--from <str> — исходная валюта

--to <str> — целевая валюта

Пример:

python -m valutatrade_hub.cli.interface get-rate \
  --from BTC \
  --to USD


Вывод (пример):

{'rate': 78519, 'updated_at': '2026-02-02T23:29:05.226661Z'}

📊 show-rates — показать курсы валют из кеша

Отображает курсы валют, сохранённые в локальном кеше (rates.json), с возможностью фильтрации.

Аргументы (все опциональные):

--currency <str> — показать курсы только для указанной валюты

--top <int> — показать N самых дорогих валют

--base <str> — показать курсы относительно базовой валюты

Примеры:

python -m valutatrade_hub.cli.interface show-rates
python -m valutatrade_hub.cli.interface show-rates --currency BTC
python -m valutatrade_hub.cli.interface show-rates --top 3

🔄 update-rates — обновить курсы валют

Загружает свежие курсы от внешних API и сохраняет их в локальный кеш.

Аргументы (опционально):

--source <str> — источник курсов
Возможные значения: coingecko, exchangerate
(по умолчанию используются оба)

Примеры:

python -m valutatrade_hub.cli.interface update-rates
python -m valutatrade_hub.cli.interface update-rates --source coingecko

⚠️ Обработка ошибок (поддерживается)

неизвестная валюта

отсутствие активной сессии

недостаточно средств

пустой или устаревший кеш курсов