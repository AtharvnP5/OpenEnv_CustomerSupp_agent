import asyncio
import os
import requests
import time
from openai import OpenAI

# USE ENV VARIABLES
API_BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o-mini"
HF_TOKEN = os.getenv("HF_TOKEN")

SPACE_URL = "https://arrowman123-customer-supp-env.hf.space"

MAX_STEPS = 20


# OPENAI AGENT 
def get_model_message(client, state):
    prompt = f"""
You are a customer support agent.

State:
{state}

Choose ONLY one word:
refund / replace / reject / ask_proof
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip().lower()


#  SAFE REQUEST
def safe_post(url, json=None):
    for _ in range(3):
        try:
            return requests.post(url, json=json, timeout=10)
        except:
            time.sleep(2)
    raise Exception("Failed request")


# MAIN 
async def main():
    client = OpenAI()

    # RESET
    res = safe_post(f"{SPACE_URL}/reset")
    result = res.json()

    state = result["observation"]["echoed_message"]
    done = result["done"]

    for step in range(1, MAX_STEPS + 1):
        if done:
            break

        message = get_model_message(client, state)

        res = safe_post(
            f"{SPACE_URL}/step",
            json={"message": message}
        )
        result = res.json()

        reward = result.get("reward", 0.0)
        done = result.get("done", False)
        state = result["observation"]["echoed_message"]

        print(f"[STEP {step}] action={message} reward={reward}")


if __name__ == "__main__":
    asyncio.run(main())