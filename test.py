import pprint

from valutatrade_hub.core.usecases import get_rate

try:
    result = get_rate("USD", "EUR")
    pprint.pprint(result)
except Exception as e:
    print(f"Ошибка: {e}")