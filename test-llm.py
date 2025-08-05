import asyncio
from openai import AsyncOpenAI
import random
import time

# --- Config ---
endpoint = "http://localhost:8000/v1"
api_key = "dummy"
model = "dummy"
chat_msg = "Halo, apa kabar?"
num_requests = 50
concurrency = 10
show_output = False  # Set True to see responses


async def run_chat(client, model_, message_):
    try:
        msg = [
            {"role": "system", "content": "Answer anything in Bahasa Indonesia."},
            {"role": "user", "content": message_}
        ]

        combined_text = ""
        response = await client.chat.completions.create(
            model=model_,
            messages=msg,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                combined_text += chunk.choices[0].delta.content

        if show_output:
            print("Response:", combined_text)

    except Exception as e:
        print("Error:", e)


async def bound_task(sem, client, model_, message_):
    async with sem:
        await run_chat(client, model_, message_)
        await asyncio.sleep(random.uniform(0.1, 0.3))  # Optional: simulate natural delay


async def stress_test():
    sem = asyncio.Semaphore(concurrency)
    client = AsyncOpenAI(base_url=endpoint, api_key=api_key)

    tasks = [
        bound_task(sem, client, model, chat_msg)
        for _ in range(num_requests)
    ]

    print(f"Starting stress test with {num_requests} requests and concurrency={concurrency}")
    start_time = time.time()
    await asyncio.gather(*tasks)
    print(f"Completed in {time.time() - start_time:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(stress_test())
