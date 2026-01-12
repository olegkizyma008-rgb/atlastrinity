import asyncio
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.db.manager import db_manager
from src.brain.logger import logger
from src.brain.memory import long_term_memory
from src.brain.orchestrator import Trinity


async def main():
    print("--- Запуск Складного Тестового Проекту: 'Атономний Крипто-Звіт' ---")

    # 1. Initialize core services
    try:
        if db_manager:
            await db_manager.initialize()
    except Exception as e:
        print(f"Попередження при ініціалізації: {e}")

    trinity = Trinity()

    # Simple complex task in Ukrainian as the user would speak it
    user_request = "Знайди сьогоднішній курс Bitcoin до USD та останні новини, розрахуй скільки коштує 0.5 BTC у гривнях, створи звіт Crypto_Report.md на Робочому столі з таблицею новин і відкрий його для перевірки."

    print(f"\nЗапит: {user_request}\n")
    print("Система починає роботу (Атлас формує стратегію...)\n")

    try:
        result = await trinity.run(user_request)

        print("\n" + "=" * 50)
        print("ФІНАЛЬНИЙ РЕЗУЛЬТАТ:")
        status = result.get("status")
        print(f"Статус: {'УСПІХ' if status == 'completed' else 'ПОМИЛКА'}")

        if status == "completed":
            if result.get("type") == "chat":
                print(f"Відповідь: {result.get('result')}")
            else:
                steps = result.get("result", [])
                print(f"Виконано кроків: {len(steps)}")
                for i, r in enumerate(steps):
                    s_icon = "✅" if r.get("success") else "❌"
                    print(f"  {i+1}. {s_icon} {r.get('action')}")
        else:
            print(f"Помилка: {result.get('error')}")
        print("=" * 50)

    except Exception as e:
        print(f"\nКритична помилка під час виконання: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Ensure logs aren't too noisy for stdout but visible
    import logging

    logging.getLogger("brain").setLevel(logging.INFO)

    asyncio.run(main())
