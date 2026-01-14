#!/usr/bin/env python3
"""Главная точка входа для ValutaTrade Hub."""
import sys
import os
from valutatrade_hub.cli.interface import ValutaTradeCLI


def main():
    """Основная функция приложения."""
    # Добавляем текущую директорию в путь для импортов
    sys.path.insert(0, os.path.dirname(__file__))

    try:
        # Инициализируем логирование (если модуль существует)
        try:
            from valutatrade_hub.logging_config import setup_logging

            setup_logging()
            print("✅ Логирование инициализировано")
        except ImportError:
            print("⚠️  Модуль логирования не найден, продолжаем без логирования")

        # Запускаем CLI
        cli = ValutaTradeCLI()
        cli.cmdloop()

    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
