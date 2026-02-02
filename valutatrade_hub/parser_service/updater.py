from datetime import datetime
from valutatrade_hub.logging_config import logger
from valutatrade_hub.core.exceptions import ApiRequestError


class RatesUpdater:
    def __init__(self, clients: list, storage):
        self.clients = clients
        self.storage = storage

    def run_update(self):
        logger.info("Starting rates update...")

        all_rates = {}
        history_entries = []

        for client in self.clients:
            name = client.__class__.__name__
            try:
                rates = client.fetch_rates()
                logger.info(f"{name}: OK ({len(rates)} rates)")
                all_rates.update(rates)

                for pair, obj in rates.items():
                    history_entries.append({
                        "id": f"{obj['from_currency']}_{obj['to_currency']}_{obj['timestamp']}",
                        **obj
                    })

            except ApiRequestError as e:
                logger.error(f"{name} failed: {e}")
                continue

        if not all_rates:
            logger.error("No rates fetched. Update aborted.")
            return

        existing = self.storage.load_rates()
        existing_pairs = existing.get("pairs", {})

        for pair, obj in all_rates.items():
            existing_pairs[pair] = {
                "rate": obj["rate"],
                "updated_at": obj["timestamp"],
                "source": obj["source"],
            }

        final = {
            "pairs": existing_pairs,
            "last_refresh": datetime.utcnow().isoformat() + "Z",
        }

        self.storage.save_rates(final)
        self.storage.append_history(history_entries)

        logger.info(f"Update completed, {len(all_rates)} pairs updated.")

        return final