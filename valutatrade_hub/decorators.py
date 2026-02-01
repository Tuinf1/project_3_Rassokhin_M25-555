# valutatrade_hub/core/decorators.py

import logging
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


def log_action(action: str, verbose: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.utcnow().isoformat()
            user = kwargs.get("user") or args[0] if args else "unknown"
            currency = kwargs.get("currency") or kwargs.get("currency_code") or "-"
            amount = kwargs.get("amount", "-")
            base = kwargs.get("base", "-")
            rate = kwargs.get("rate", "-")

            try:
                result = func(*args, **kwargs)
                logger.info(
                    f"{timestamp} {action.upper()} user='{user}' currency='{currency}' "
                    f"amount={amount} rate={rate} base={base} result=OK"
                )
                return result
            except Exception as e:
                logger.info(
                    f"{timestamp} {action.upper()} user='{user}' currency='{currency}' "
                    f"amount={amount} rate={rate} base={base} result=ERROR error_type={type(e).__name__} error_msg='{e}'"
                )
                raise
        return wrapper
    return decorator