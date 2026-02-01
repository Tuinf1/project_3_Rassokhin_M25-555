# valutatrade_hub/core/logging_config.py

# import logging
# from logging.handlers import RotatingFileHandler
# import os

# log_dir = "logs"
# os.makedirs(log_dir, exist_ok=True)

# log_path = os.path.join(log_dir, "actions.log")

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(levelname)s %(message)s",
#     handlers=[
#         RotatingFileHandler(log_path, maxBytes=500_000, backupCount=3),
#         logging.StreamHandler()
#     ]
# )


import logging
from logging.handlers import RotatingFileHandler
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "actions.log")

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

file_handler = RotatingFileHandler(log_path, maxBytes=500_000, backupCount=3)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()  # 💥 сбрасываем предыдущие обработчики!
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Проверка
# logger.info("Тест: логирование включено")
