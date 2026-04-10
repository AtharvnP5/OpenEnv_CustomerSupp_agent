import asyncio
import os
import requests
import time
from openai import OpenAI

# REQUIRED ENV VARIABLES
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

API_KEY = os.getenv("API_KEY", HF_TOKEN)

SPACE_URL  = "https://arrowman123-customer-supp-env.hf.space"
BENCHMARK  = "openenv"
MAX_STEPS  = 20

TASK_NAMES = ["easy", "medium", "hard"]


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
        print(f"[ERROR] LLM failed: {e}", flush=True)
        return "reject"


# SAFE REQUEST
def safe_post(url, json=None, retries=3):
    for i in range(retries):
        try:
            return requests.post(url, json=json, timeout=10)
        except Exception as e:
            print(f"[DEBUG] retry {i+1} due to {e}", flush=True)
            time.sleep(2)
    raise Exception("Failed after retries")

def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error=None):
    error_str = "null" if error is None else str(error)
    done_str  = "true" if done else "false"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={done_str} error={error_str}",
        flush=True
    )

def log_end(success, steps, score, rewards):
    success_str = "true" if success else "false"
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={success_str} steps={steps} score={score:.4f} rewards={rewards_str}", flush=True)


# MAIN
async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    for task_name in TASK_NAMES:
        step_rewards = []
        score        = 0.5
        success      = False

        log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

        try:
            res    = safe_post(f"{SPACE_URL}/reset", json={"task": task_name})
            result = res.json()

            state = result["observation"]["echoed_message"]
            done  = result["done"]

            for step in range(1, MAX_STEPS + 1):
                if done:
                    break

                action = get_model_message(client, state)

                res    = safe_post(f"{SPACE_URL}/step", json={"message": action})
                result = res.json()

                state  = result["observation"]["echoed_message"]
                done   = result["done"]
                reward = float(result.get("reward", 0.0))

                step_rewards.append(reward)

                log_step(step=step, action=action, reward=reward, done=done, error=None)

            raw_score = float(result.get("info", {}).get("score", 0.5))
            score     = max(0.05, min(0.95, raw_score))
            success   = True

        except Exception as e:
            print(f"[ERROR] task={task_name} {e}", flush=True)
            score = 0.1

        finally:
            log_end(success=success, steps=len(step_rewards), score=score, rewards=step_rewards)


if __name__ == "__main__":
    asyncio.run(main())