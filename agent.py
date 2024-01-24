# rl_agent.py
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers

class QLearningAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.model = self._build_model()

    def _build_model(self):
        model = tf.keras.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.state_size),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def act(self, state):
        # Choose an action based on epsilon-greedy strategy
        # For simplicity, let's use a random action for now
        return np.random.choice(self.action_size)

    def train(self, state, action, reward, next_state, done):
        # Q-learning update rule
        target = reward
        if not done:
            # Use the Q-network to estimate the future discounted reward
            target += gamma * np.amax(self.model.predict(next_state)[0])

        # Get the current Q-values
        target_f = self.model.predict(state)
        
        # Update the Q-value of the chosen action
        target_f[0][action] = target

        # Train the Q-network on the updated Q-values
        self.model.fit(state, target_f, epochs=1, verbose=0)

    def save_model(self, model_path):
        # Save the trained model
        self.model.save(model_path)

    def load_model(self, model_path):
        # Load a pre-trained model
        self.model = tf.keras.models.load_model(model_path)
