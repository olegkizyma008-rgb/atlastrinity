import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.orchestrator import Trinity  # noqa: E402


async def test_speak():
    print("--- TTS Testing ---")
    trinity = Trinity()
    # Mock state to avoid log crash
    trinity.state = {"logs": [], "messages": []}

    text = "Привіт! Це перевірка голосу Тетяни. Якщо ви це чуєте, значить аудіо працює."
    print(f"Speaking: {text}")
    try:
        await trinity._speak("tetyana", text)
        print("Successfully called _speak")
    except Exception as e:
        print(f"Error during _speak: {e}")

    print("Done testing.")


if __name__ == "__main__":
    asyncio.run(test_speak())
