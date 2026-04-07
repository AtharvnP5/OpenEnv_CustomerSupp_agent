from environment import SupportEnv
from dataset import cases   # your dataset file

env = SupportEnv(cases)

obs = env.reset()
done = False

while not done:
    print(obs)

    action = input("Enter action: ")   # simulate agent

    obs, reward, done = env.step(action)

    print(f"Reward: {reward}")
    print("-" * 40)