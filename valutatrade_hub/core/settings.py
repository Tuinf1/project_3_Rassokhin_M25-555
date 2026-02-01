# valutatrade_hub/core/settings.py

import tomli
from pathlib import Path
from typing import Any

class SettingsLoader:
    _instance = None
    _config: dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().new(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        pyproject = Path("pyproject.toml")
        if not pyproject.exists():
            self._config = {}
            return

        with pyproject.open("rb") as f:
            parsed = tomli.load(f)

        self._config = parsed.get("tool", {}).get("valutatrade", {})

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def reload(self):
        self._load_config()