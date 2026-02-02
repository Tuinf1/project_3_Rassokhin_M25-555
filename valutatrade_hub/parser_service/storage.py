import json
import os
from tempfile import NamedTemporaryFile


class Storage:
    def init(self, config):
        self.config = config

    def load_rates(self) -> dict:
        """
        Загрузка файла rates.json.
        Возвращает структуру вида:
        {
            "pairs": {
                "BTC_USD": { "rate": ..., "updated_at": ..., "source": ... },
                ...
            },
            "last_refresh": "..."
        }
        """
        if not os.path.exists(self.config.RATES_FILE_PATH):
            return {"pairs": {}, "last_refresh": None}

        with open(self.config.RATES_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_rates(self, data: dict):
        """
        Безопасно сохраняет словарь в rates.json
        """
        tmp = NamedTemporaryFile("w", delete=False, encoding="utf-8")
        json.dump(data, tmp, indent=2, ensure_ascii=False)
        tmp.close()
        os.replace(tmp.name, self.config.RATES_FILE_PATH)

    def update_rate_pair(self, pair: str, new_entry: dict):
        """
        Обновляет курс конкретной пары, если он свежее.
        new_entry должен содержать: rate, updated_at, source
        """
        data = self.load_rates()
        current = data["pairs"].get(pair)

        if (
            not current or
            new_entry["updated_at"] > current.get("updated_at", "")
        ):
            data["pairs"][pair] = new_entry
            data["last_refresh"] = new_entry["updated_at"]
            self.save_rates(data)

    def append_history(self, entries: list[dict]):
        """
        Добавляет список новых записей в exchange_rates.json, 
        если у них уникальный id.
        """
        history = []
        if os.path.exists(self.config.HISTORY_FILE_PATH):
            with open(self.config.HISTORY_FILE_PATH, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []

        existing_ids = {item["id"] for item in history}
        new_entries = [e for e in entries if e["id"] not in existing_ids]
        if not new_entries:
            return  # нечего добавлять

        history.extend(new_entries)

        tmp = NamedTemporaryFile("w", delete=False, encoding="utf-8")
        json.dump(history, tmp, indent=2, ensure_ascii=False)
        tmp.close()
        os.replace(tmp.name, self.config.HISTORY_FILE_PATH)