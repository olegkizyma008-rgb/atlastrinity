import sys
import time

import requests

BASE_URL = "http://127.0.0.1:8000"


def wait_for_server():
    print("Waiting for server to be ready...")
    for _ in range(30):
        try:
            resp = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if resp.status_code == 200:
                print("Server is UP!")
                return True
        except Exception:
            pass
        time.sleep(1)
    print("Server failed to start.")
    return False


def run_task(task_prompt: str, task_name: str):
    print(f"\n\n--- Running Task: {task_name} ---")
    print(f"Prompt: {task_prompt}")

    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={"request": task_prompt}, timeout=300)
        if response.status_code == 200:
            result = response.json()
            status = result.get("status")
            print(f"Status: {status}")
            output = str(result.get("result"))
            print(f"Output Preview: {output[:300]}...")
            if status == "error":
                print("!!! TASK FAILED !!!")
        else:
            print(f"HTTP Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Request Error: {e}")


def main():
    if not wait_for_server():
        sys.exit(1)

    # 1. Simple Logic / Output Truncation Check
    run_task(
        "Count from 1 to 50000 and output all numbers (test truncation).",
        "Large Output Logic",
    )

    # 2. File Creation & Verification (Common Grisha Task)
    run_task(
        "Create a python script named 'hello_universe.py' in the current folder that prints 'Hello Universe' 5 times, then run it.",
        "File Creation & Execution",
    )

    # 3. System Info (Grisha Verification)
    run_task("What is the uptime of this computer?", "System Info")


if __name__ == "__main__":
    main()
