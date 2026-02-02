from api_clients import CoinGeckoClient, ExchangeRateApiClient
from config import ParserConfig
from storage import Storage
from updater import RatesUpdater

config = ParserConfig()
storage = Storage(config)
clients = [CoinGeckoClient(config), ExchangeRateApiClient(config)]

updater = RatesUpdater(clients, storage)
result = updater.run_update()
print(result)