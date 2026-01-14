# ValutaTrade Hub

Платформа для симуляции торговли валютами и криптовалютами.

## Возможности

-  Торговля фиатными валютами (USD, EUR, RUB, GBP, JPY, CNY)
-  Торговля криптовалютами (BTC, ETH, LTC, XRP)  
-  Реальные курсы валют через API
-  Регистрация и аутентификация пользователей
-  Просмотр портфеля с красивыми таблицами
-  Автоматическое обновление курсов

##  Структура проекта

valutatrade_hub/
├── core/ # Бизнес-логика
│ ├── models.py # Модели User, Wallet, Portfolio
│ ├── usecases.py # Бизнес-сценарии
│ ├── exceptions.py # Кастомные исключения
│ └── currencies.py # Реестр валют
├── infra/ # Инфраструктура
│ ├── database.py # Менеджер базы данных (JSON)
│ └── settings.py # Загрузчик настроек
├── parser_service/ # Сервис парсинга курсов
│ ├── api_clients.py # Клиенты API (CoinGecko, ExchangeRate-API)
│ ├── updater.py # Обновление курсов
│ ├── config.py # Конфигурация парсера
│ └── scheduler.py # Планировщик обновлений
├── cli/ # Командный интерфейс
│ └── interface.py # Основной CLI
└── data/ # Данные (JSON файлы)
├── users.json # Пользователи
├── portfolios.json # Портфели
└── rates.json # Курсы валют


### Установка
make install

### Запуск 
make project
# или
poetry run python main.py

### Основные команды

Команда	                Описание	            Пример
register <user> <pass>	Регистрация	            register john secret123
login <user> <pass>	    Вход	                login john secret123
show-portfolio	        Портфель	            show-portfolio
buy <curr> <amount>	    Купить валюту	        buy EUR 100
sell <curr> <amount>	Продать валюту	        sell BTC 0.5
get-rate <from> <to>	Курс валют	            get-rate EUR USD
update-rates	        Обновить курсы	        update-rates
exit	                Выход	                exit

### API_KEY
 EXCHANGERATE_API_KEY="a420cb9beea6876367c5caab"

### asciinema
##  Демонстрация работы проекта 
 https://asciinema.org/a/3txQNHjopMaiE1NHffzOQYu1G