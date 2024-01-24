# train_agent.py
import numpy as np

epsilon = 1.0
epsilon_decay = 0.995
gamma = 0.95
num_episodes = 1000
width,height=1200,600
from env import CustomEnv
from agent import QLearningAgent

# Inside your training loop
env = CustomEnv()
agent = QLearningAgent(state_size=(height, width, 3), action_size=4)
count = 0
print("Reached here")
for episode in range(num_episodes):
    state = env.reset()
    state = np.reshape(state, (1, height, width, 3))

    total_reward = 0

    while True:
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        next_state = np.reshape(next_state, (1, height, width, 3))

        agent.train(state, action, reward, next_state, done, gamma)

        total_reward += reward
        state = next_state
        env.run_game_loop(action)
        if done:
            break

    # Decay exploration rate
    epsilon *= epsilon_decay
    epsilon = max(0.1, epsilon)  # Ensure minimum exploration

    print(f"Episode: {episode + 1}, Total Reward: {total_reward}")

# Save the trained model
agent.save_model("trained_model.h5")