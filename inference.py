import asyncio
import os
import requests
import time
from openai import OpenAI   

# REQUIRED VARIABLES
API_BASE_URL = os.environ["API_BASE_URL"]   
API_KEY = os.environ["API_KEY"]             
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

SPACE_URL = "https://arrowman123-customer-supp-env.hf.space"

TASK_NAME = "customer-support"
BENCHMARK = "openenv"

MAX_STEPS = 20
MAX_TOTAL_REWARD = 20
SUCCESS_SCORE_THRESHOLD = 0.6


# LLM AGENT 
def get_model_message(client, state):
    prompt = f"""
You are a customer support agent.

State:
{state}

Choose ONLY ONE word:
refund / replace / reject / ask_proof
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return "reject"   # fallback


# SAFE REQUEST
def safe_post(url, json=None, retries=3):
    for i in range(retries):
        try:
            return requests.post(url, json=json, timeout=10)
        except Exception as e:
            print(f"[DEBUG] retry {i+1} due to {e}")
            time.sleep(2)
    raise Exception("Failed after retries")


# LOGGING
def log_start(**kwargs):
    print("[START]", kwargs, flush=True)

def log_step(**kwargs):
    print("[STEP]", kwargs, flush=True)

def log_end(**kwargs):
    print("[END]", kwargs, flush=True)


# MAIN
async def main():
    rewards = []
    steps_taken = 0
    success = False

    # Initialize client using THEIR proxy
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY
    )

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        res = safe_post(f"{SPACE_URL}/reset")
        result = res.json()

        state = result["observation"]["echoed_message"]
        done = result["done"]

        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            #  USE LLM
            message = get_model_message(client, state)

            res = safe_post(
                f"{SPACE_URL}/step",
                json={"message": message}
            )
            result = res.json()

            reward = result.get("reward", 0.0)
            done = result.get("done", False)
            state = result["observation"]["echoed_message"]

            rewards.append(reward)
            steps_taken = step

            log_step(
                step=step,
                action=message,
                reward=reward,
                done=done,
                error=None
            )

        score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = max(0.0, min(1.0, score))
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        log_end(
            success=success,
            steps=steps_taken,
            score=score if 'score' in locals() else 0.0,
            rewards=rewards
        )


if __name__ == "__main__":
    asyncio.run(main())
