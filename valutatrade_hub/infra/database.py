from __future__ import annotations
import json
from pathlib import Path
from threading import Lock
from typing import Any
from .settings import settings


class DatabaseManager:
    _instance = None

    def new(cls):
        if cls._instance is None:
            cls._instance = super().new(cls)
            cls._instance._initialized = False
        return cls._instance

    def init(self):
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        self._lock = Lock()
        self.users_file = Path(settings.get('USERS_FILE'))
        self.portfolios_file = Path(settings.get('PORTFOLIOS_FILE'))
        self.rates_file = Path(settings.get('RATES_FILE'))
        # ensure files exist
        for p in (self.users_file, self.portfolios_file, self.rates_file):
            if not p.exists():
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps([]) if p != self.rates_file else json.dumps({}), encoding='utf-8')

    def _read_json(self, path: Path, default: Any):
        with self._lock:
            try:
                text = path.read_text(encoding='utf-8')
                return json.loads(text) if text.strip() else default
            except Exception:
                return default

    def _write_json(self, path: Path, data: Any):
        with self._lock:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def load_users(self) -> list[dict]:
        return self._read_json(self.users_file, [])

    def save_users(self, users: list[dict]):
        self._write_json(self.users_file, users)

    def load_portfolios(self) -> list[dict]:
        return self._read_json(self.portfolios_file, [])

    def save_portfolios(self, portfolios: list[dict]):
        self._write_json(self.portfolios_file, portfolios)

    def load_rates(self) -> dict:
        return self._read_json(self.rates_file, {})

    def save_rates(self, rates: dict):
        self._write_json(self.rates_file, rates)

    def update_json(self, path: Path, default: Any, modify_fn: callable):
        with self._lock:
            try:
                text = path.read_text(encoding='utf-8')
                data = json.loads(text) if text.strip() else default
            except Exception:
                data = default

            modify_fn(data)  #

            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def fetch_and_update_rates(self) -> dict:
        rates = self.load_rates()

        import datetime
        now = datetime.datetime.utcnow().isoformat()
        if isinstance(rates, dict):
            rates['last_refresh'] = now
            self.save_rates(rates)
            return rates
        raise RuntimeError('Rates storage malformed')


db = DatabaseManager()