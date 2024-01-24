import gym
import numpy as np
from  new_env import CustomEnv  # Assuming your environment file is named custom_env.py
from dqn_agent import DQNAgent  # Assuming your DQN agent class is named DQNAgent and it's in a file named dqn_agent.py

def train_dqn_agent(env, num_episodes=1000, exploration_rate=1.0, exploration_decay=0.995, min_exploration_rate=0.1):
    state_shape = env.observation_space.shape
    state_shape = env.observation_space.shape
    num_actions = env.action_space.n

    agent = DQNAgent(state_shape, num_actions)

    for episode in range(num_episodes):
        state = env.reset()
        state = np.expand_dims(state, axis=0)  # Add batch dimension

        total_reward = 0
        done = False

        while not done:
            action = agent.select_action(state)

            next_state, reward, done, _ = env.step(action)
            next_state = np.expand_dims(next_state, axis=0)  # Add batch dimension

            agent.buffer.append((state, action, reward, next_state, done))
            agent.train()

            total_reward += reward
            state = next_state
        env.render()
        # Decay exploration rate
        exploration_rate *= exploration_decay
        exploration_rate = max(min_exploration_rate, exploration_rate)
        print(f"Episode: {episode + 1}, Total Reward: {total_reward}")

    env.close()

if __name__ == "__main__":
    custom_env = CustomEnv()
    train_dqn_agent(custom_env)
