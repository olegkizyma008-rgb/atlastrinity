
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain.orchestrator import Trinity
from src.brain.logger import logger

async def run_dev_mode_movie_test():
    print("--- 🎬 DEV MODE TEST: MOVIE TASK 🎬 ---")
    
    trinity = Trinity()
    await trinity.initialize()
    
    # Direct speech prompt as requested
    prompt = "Відкрий Safari, введи в пошук 'watch Ex Machina online' і відкрий перше посилання."
    print(f"\nUser Request: {prompt}\n")
    
    # We use a slightly higher timeout to allow for the browser interactions
    result = await trinity.run(prompt)
    
    print("\n--- MISSION STATUS ---")
    print(f"Status: {result.get('status')}")
    if result.get('error'):
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    try:
        asyncio.run(run_dev_mode_movie_test())
    except KeyboardInterrupt:
        print("\nMission Aborted.")
