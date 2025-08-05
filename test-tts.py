from openai import OpenAI
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# ==== Configuration (Edit if needed) ====
endpoint = "http://43.218.81.123:8003/v1"
model = "dummy"
text = "Hello, how are you?"
voice = "ono"
num_requests = 10
concurrency = 2
check_only = False
# ========================================

def check_endpoint(endpoint):
    try:
        response = requests.get(f"{endpoint}/docs", timeout=5)
        is_active = response.status_code == 200
        print(f"Endpoint status: {'Active' if is_active else 'Inactive'}")
        return is_active
    except Exception as e:
        print(f"Endpoint check failed: {e}")
        return False

def send_tts_request(index):
    try:
        client = OpenAI(base_url=endpoint, api_key="dummy")
        response = client.audio.speech.create(
            model=model,
            input=text,
            voice=voice,
        )

        # Stream to /dev/null equivalent (discard output)
        if hasattr(response, '__iter__'):
            for _ in response:
                pass
        else:
            _ = response.content  # discard

        return True, f"Request {index} success"
    except Exception as e:
        return False, f"Request {index} failed: {e}"

def stress_test():
    results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_tts_request, i) for i in range(num_requests)]

        for future in as_completed(futures):
            success, result = future.result()
            results.append((success, result))

    duration = time.time() - start_time
    success_count = sum(1 for r in results if r[0])
    fail_count = len(results) - success_count

    print(f"\nCompleted {len(results)} requests in {duration:.2f}s")
    print(f"Successful: {success_count}, Failed: {fail_count}")

    if fail_count > 0:
        for ok, err in results:
            if not ok:
                print(f"[ERROR] {err}")

if __name__ == "__main__":
    if check_only:
        check_endpoint(endpoint)
    else:
        stress_test()
