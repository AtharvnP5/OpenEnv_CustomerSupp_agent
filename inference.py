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


#  LLM AGENT 
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
        print(f"[ERROR] LLM failed: {e}")
        return "reject"


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


async def main():
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY
    )

    task_scores = []

    try:
        # run 3 tasks
        for task_idx in range(3):
            # 1. Log the START of each individual task with a unique ID
            current_task_name = f"{TASK_NAME}-{task_idx}"
            log_start(task=current_task_name, env=BENCHMARK, model=MODEL_NAME)

            res = safe_post(f"{SPACE_URL}/reset")
            result = res.json()

            state = result["observation"]["echoed_message"]
            done = result["done"]
            
            steps_taken = 0

            for step in range(1, MAX_STEPS + 1):
                steps_taken = step
                if done:
                    break

                message = get_model_message(client, state)

                res = safe_post(
                    f"{SPACE_URL}/step",
                    json={"message": message}
                )
                result = res.json()

                state = result["observation"]["echoed_message"]
                done = result["done"]

                log_step(
                    step=step,
                    action=message,
                    reward=result.get("reward", 0.0),
                    done=done,
                    error=None
                )

            #  GET SCORE FROM ENV
            score = result.get("score", 0.5)
            
            # This clamp is correct and fixes your second error!
            score = max(0.01, min(0.99, score)) 
            task_scores.append(score)

            # 2. Log the END of each individual task
            log_end(
                success=True,
                steps=steps_taken, # Log steps per task, not total tasks
                score=score
            )

        # Optional: Print final average for your own debugging
        final_score = sum(task_scores) / len(task_scores)
        print(f"[DEBUG] All tasks completed. Final Average Score: {final_score}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(main())
