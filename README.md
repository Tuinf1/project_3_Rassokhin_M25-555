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




📌 Список CLI-команд valutatrade_hub
🔐 register — регистрация нового пользователя

Создаёт нового пользователя и инициализирует пустой портфель.

Аргументы:

--username <str> — имя пользователя

--password <str> — пароль (минимум 4 символа)

Пример:

register --username alice --password 1234

🔑 login — авторизация пользователя

Сохраняет сессию текущего пользователя.

Аргументы:

--username <str>

--password <str>

Пример:

login --username alice --password 1234

🚪 logout — выход из системы

Завершает текущую сессию (удаляет session.json).

Аргументы: отсутствуют

Пример:

logout

💼 show-portfolio — просмотр портфеля

Показывает все кошельки пользователя и их стоимость в базовой валюте.

Аргументы:

--base <str> — базовая валюта (по умолчанию USD)

Пример:

show-portfolio --base USD

💰 buy — покупка валюты

Покупка указанной валюты по текущему курсу из кеша.

Аргументы:

--currency <str> — код валюты (например, BTC)

--amount <float> — количество для покупки

Пример:

buy --currency BTC --amount 0.01

💸 sell — продажа валюты

Продажа валюты из кошелька с расчётом выручки в USD.

Аргументы:

--currency <str> — код валюты

--amount <float> — количество для продажи

Пример:

sell --currency BTC --amount 0.005

📈 get-rate — получить курс между двумя валютами

Возвращает актуальный курс из локального кеша с учётом TTL.

Аргументы:

--from <str> — исходная валюта

--to <str> — целевая валюта

Пример:

get-rate --from BTC --to USD

📊 show-rates — показать курсы валют из кеша

Отображает список доступных курсов с возможностью фильтрации.

Аргументы (опционально):

--currency <str> — показать курсы только для указанной валюты

--top <int> — показать N самых дорогих валют

--base <str> — фильтр по базовой валюте (например, USD, EUR)

Примеры:

show-rates
show-rates --currency BTC
show-rates --top 3

🔄 update-rates — обновить курсы валют

Загружает свежие курсы от внешних API и сохраняет их в локальный кеш.

Аргументы (опционально):

--source <str> — источник курсов (coingecko, exchangerate)

Пример:

update-rates
update-rates --source coingecko
