import io
import time
import soundfile as sf
import argparse
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_audio(audio_file_path):
    audio_data, sample_rate = sf.read(audio_file_path)
    audio_bytes = io.BytesIO()
    sf.write(audio_bytes, audio_data, sample_rate, format='wav')
    return audio_bytes.getvalue()

def send_request(audio_bytes, endpoint):
    client = OpenAI(base_url=endpoint, api_key="dummy")

    try:
        response = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes, "audio/wav"),
            model="dummy",
            language="id"
        )
        return True, response.text
    except Exception as e:
        return False, str(e)

def stress_test(audio_path, endpoint, num_requests=100, concurrency=10):
    audio_bytes = load_audio(audio_path)
    results = []

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request, audio_bytes, endpoint) for _ in range(num_requests)]

        for future in as_completed(futures):
            success, result = future.result()
            results.append((success, result))

    duration = time.time() - start_time
    success_count = sum(1 for r in results if r[0])
    fail_count = len(results) - success_count

    print(f"Completed {len(results)} requests in {duration:.2f}s")
    print(f"Successful: {success_count}, Failed: {fail_count}")

    if fail_count > 0:
        for ok, err in results:
            if not ok:
                print(f"[ERROR] {err}")

if __name__ == "__main__":
    endpoint = "http://108.137.61.143:8001/v1"
    audio_file = "audio.wav"
    requests_count = 10
    concurrency_level = 2

    stress_test(audio_file, endpoint, requests_count, concurrency_level)
