"""Simple smoke test for the deployed DjangoDesk API.

Usage:
    uv run python scripts/smoke.py https://your-app.onrender.com
"""

import json
import sys
import urllib.request


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/smoke.py <base-url>")
        return 1

    base_url = sys.argv[1].rstrip("/")
    health_url = f"{base_url}/health"

    print(f"Checking: {health_url}")

    try:
        with urllib.request.urlopen(health_url, timeout=60) as response:
            status_code = response.status
            body = json.loads(response.read().decode("utf-8"))

        if status_code == 200 and body.get("status") == "ok":
            print("SMOKE TEST PASSED")
            print(f"HTTP Status: {status_code}")
            print(f"Application: {body.get('app')}")
            print(f"Version: {body.get('version')}")
            return 0

        print("SMOKE TEST FAILED")
        print(f"HTTP Status: {status_code}")
        print(f"Response: {body}")
        return 1

    except Exception as error:
        print("SMOKE TEST FAILED")
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
