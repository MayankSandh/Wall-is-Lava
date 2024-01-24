# custom_env.py
import gym
from gym import spaces
import numpy as np
from graphics import setup_map, raycast, movements
import pygame
import math
width,height=1200,600
class CustomEnv(gym.Env):
    def __init__(self):
        super(CustomEnv, self).__init__()

        # Define observation space (assuming RGB images)
        self.observation_space = spaces.Box(low=0, high=255, shape=(height, width, 3), dtype=int)

        # Define action space (WASD controls)
        self.action_space = spaces.Discrete(4)

        # Other initialization logic goes here
        pygame.init()
        self.root = pygame.display.set_mode((width, height))
        pygame.mouse.set_visible(False)

        self.gameover = False
        self.clock = pygame.time.Clock()

        self.coords = [1.5, 1.5]
        self.angle = 0
        self.fov = math.pi / 3
        self.max_depth = 10
        self.number_of_rays = width
        self.delta_angle = self.fov / self.number_of_rays

        self.scale = width // self.number_of_rays
        self.screen_distance = (width / 2) / math.tan(self.fov / 2)

        self.move = 0.060
        self.rotate = 10

        self.objects = {}
        self.colors = {1: (255, 0, 0), 2: (0, 0, 255), 3: (0, 255, 0)}

    def reset(self):
        """
        Reset the game and return the initial state.
        """
        pygame.mouse.set_visible(False)
        self.gameover = False

        # ... (any other reset logic)

        return self._get_state()

    def _get_state(self):
        """
        Capture the current game state as an image and return it.
        """
        game_state = pygame.surfarray.array3d(self.root)
        return np.array(game_state)

    def step(self, action):
        """
        Apply the action to the game and return the next state, reward, done, and info.
        """
        self.perform_action(action)

        next_state = self._get_state()

        # Example: Calculate reward, done, and other info based on your game logic
        reward = 0
        done = False
        info = {}

        return next_state, reward, done, info

    def render(self):
        """
        Render the game (optional).
        """
        pygame.display.flip()

    def close(self):
        """
        Close the game.
        """
        pygame.quit()

    def perform_action(self, action):
        """
        Perform the specified action in the game.
        """
        # Implement the logic to perform the action (WASD controls)
        # ...

    def run_game_loop(self):
        """
        Run the main game loop.
        """
        while not self.gameover:
            self.root.fill('black')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameover = True

            setup_map(self.root)
            raycast(self.root)
            self.movements()

            pygame.display.set_caption(str(self.clock.get_fps() // 1))

            self.clock.tick(60)
            pygame.display.update()

    def movements(self):
        """
        Handle player movements in the game.
        """
        mx = self.move * math.cos(self.angle)
        my = self.move * math.sin(self.angle)
        dx, dy = 0, 0

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            dx += mx
            dy += my
        if pressed[pygame.K_s]:
            dx += -mx
            dy += -my
        if pressed[pygame.K_a]:
            self.angle += -self.rotate * 0.002
        if pressed[pygame.K_d]:
            self.angle += self.rotate * 0.002

        if (int(self.coords[0] + dx), int(self.coords[1])) not in self.objects:
            self.coords[0] += dx
        if (int(self.coords[0]), int(self.coords[1] + dy)) not in self.objects:
            self.coords[1] += dy

        # Handle wall collisions
        # ...

# Instantiate the environment
env = CustomEnv()

# Run the game loop (this would typically be done in your main script)
env.run_game_loop()
