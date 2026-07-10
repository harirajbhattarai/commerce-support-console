import os
import requests
import json

def test_minimax():
    # Use Railway environment variables
    api_key = os.getenv("MINIMAX_API_KEY", "")

    if not api_key:
        print("MINIMAX_API_KEY environment variable is missing.")
        return

    print("MiniMax auth smoke test:")

    # Official Open Platform endpoint according to contract
    url = "https://api.minimax.io/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        status = response.status_code
        print(f"HTTP status: {status}")

        if status == 200:
            print("Authentication: PASS")
            try:
                data = response.json()
                # Check if MiniMax-M2.7 is available in the models list
                models = [m.get("id", "") for m in data.get("data", [])]
                if "MiniMax-M2.7" in models or "minimax-m2.7" in [m.lower() for m in models]:
                    print("MiniMax-M2.7 available: YES")
                else:
                    print("MiniMax-M2.7 available: NO")
            except Exception:
                print("MiniMax-M2.7 available: UNKNOWN")
        else:
            print("Authentication: FAIL")
            try:
                error_data = response.json()
                print(f"Error category: {error_data.get('message', 'unknown')} (Code: {error_data.get('http_code', 'unknown')})")
            except Exception:
                print("Error category: non_json_error_response")

    except requests.exceptions.Timeout:
        print("Error category: timeout")
    except requests.exceptions.ConnectionError:
        print("Error category: connection_error")
    except requests.exceptions.RequestException:
        print("Error category: request_error")
    except Exception:
        print("Error category: unknown_exception")

if __name__ == "__main__":
    test_minimax()
