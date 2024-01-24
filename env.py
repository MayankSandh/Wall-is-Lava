# custom_env.py
import gym
from gym import spaces
import numpy as np
from graphics import setup_map, raycast, movements
import pygame
import math
from copy import deepcopy
width,height=1200,600
class CustomEnv(gym.Env):
    def __init__(self):
        super(CustomEnv, self).__init__()

        # Define observation space (assuming RGB images)
        self.observation_space = spaces.Box(low=0, high=255, shape=(height, width, 3), dtype=np.float32)

        # Define action space (WASD controls)
        self.action_space = spaces.Discrete(4)

        # Other initialization logic goes here
        pygame.init()
        self.root = pygame.display.set_mode((width, height))
        pygame.mouse.set_visible(False)

        self.gameover = False
        self.clock = pygame.time.Clock()
        self.MAP=[
            [1,1,1,1,1,1,1,1,1,1,1,1], # top left is the origin and facing east
            [1,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,3,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,3,1],
            [1,1,1,1,1,1,1,1,1,1,1,1]
        ]
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

        self.MAP_reset = deepcopy(self.MAP)
        self.angle_reset = deepcopy(self.angle)
        self.coords_reset = deepcopy(self.coords)
        self.objects_reset = deepcopy(self.objects)
        self.action = 0

    def reset(self):
        self.MAP = deepcopy(self.MAP_reset)
        self.angle = deepcopy(self.angle_reset)
        self.objects = deepcopy(self.objects_reset)
        self.coords = deepcopy(self.coords_reset)
        self.gameover = False
        return self._get_state()

    def _get_state(self):
        game_state = pygame.surfarray.array3d(self.root)
        return np.array(game_state, dtype=np.float32)

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
        pygame.display.flip()

    def close(self):
        pygame.quit()

    def perform_action(self, action):
        mx = self.move * math.cos(self.angle)
        my = self.move * math.sin(self.angle)
        dx, dy = 0, 0

        if action == 0:
            dx += mx
            dy += my
        if action == 1:
            dx += -mx
            dy += -my
        if action == 2:
            self.angle += -self.rotate * 0.002
        if action == 3:
            self.angle += self.rotate * 0.002

        if (int(self.coords[0] + dx), int(self.coords[1])) not in self.objects:
            self.coords[0] += dx
        if (int(self.coords[0]), int(self.coords[1] + dy)) not in self.objects:
            self.coords[1] += dy
        if self.MAP[int(self.coords[1])][int(self.coords[0]+dx)] == 3: # do not update coords if I am heading into a wall
            self.objects.pop((int(self.coords[0]+dx),int(self.coords[1])))
            self.MAP[int(self.coords[1])][int(self.coords[0]+dx)] = 0
        if self.MAP[int(self.coords[1]+dy)][int(self.coords[0])] == 3:
            self.objects.pop((int(self.coords[0]),int(self.coords[1]+dy)))
            self.MAP[int(self.coords[1]+dy)][int(self.coords[0])] = 0

    def run_game_loop(self, action):
        while not self.gameover:
            self.root.fill('black')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameover = True

            self.setup_map()
            self.raycast()
            self.perform_action(action)


            pygame.display.set_caption(str(self.clock.get_fps() // 1))

            self.clock.tick(60)
            pygame.display.update()

    def movements(self):
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
        if self.MAP[int(self.coords[1])][int(self.coords[0]+dx)] == 3: # do not update coords if I am heading into a wall
            self.objects.pop((int(self.coords[0]+dx),int(self.coords[1])))
            self.MAP[int(self.coords[1])][int(self.coords[0]+dx)] = 0
            self.reset()
        if self.MAP[int(self.coords[1]+dy)][int(self.coords[0])] == 3:
            self.objects.pop((int(self.coords[0]),int(self.coords[1]+dy)))
            self.MAP[int(self.coords[1]+dy)][int(self.coords[0])] = 0
            self.reset()
    def setup_map(self):
        for i in range(len(self.MAP)):
            for j in range(len(self.MAP[i])):
                if self.MAP[i][j]:
                    self.objects[(j,i)]=self.MAP[i][j]
        pygame.draw.rect(self.root,(50,50,50),(0,height//2,width,height)) # default background
        pygame.draw.rect(self.root,(30,30,30),(0,0,width,height//2)) # default background
    def raycast(self):
        ray_angle=(self.angle-(self.fov/2))+0.000001 # error never makes this zero
        color=0 

        for ray in range(self.number_of_rays):

            sin_angle=math.sin(ray_angle)
            cos_angle=math.cos(ray_angle)

            #vertical
            x_vertical,dx=(int(self.coords[0])+1,1) if cos_angle>0 else (int(self.coords[0])-0.000001,-1)
            depth_vertical=(x_vertical-self.coords[0])/cos_angle

            y_vertical=(depth_vertical*sin_angle)+self.coords[1]

            delta_depth=dx/cos_angle
            dy=delta_depth*sin_angle

            for i in range(self.max_depth):
                tile_vertical=(int(x_vertical),int(y_vertical))
                if tile_vertical in self.objects:
                    break
                x_vertical+=dx
                y_vertical+=dy
                depth_vertical+=delta_depth

            #horizontal
            y_horizontal,dy=(int(self.coords[1])+1,1) if sin_angle>0 else (int(self.coords[1])-0.000001,-1)
            depth_horizontal=(y_horizontal-self.coords[1])/sin_angle

            x_horizontal=(depth_horizontal*cos_angle)+self.coords[0]

            delta_depth=dy/sin_angle
            dx=delta_depth*cos_angle

            for i in range(self.max_depth):
                tile_horizontal=(int(x_horizontal),int(y_horizontal))
                if tile_horizontal in self.objects:
                    break
                x_horizontal+=dx
                y_horizontal+=dy
                depth_horizontal+=delta_depth

            if depth_horizontal<depth_vertical:
                depth=depth_horizontal
                color=self.objects[tile_horizontal]
                side=0
            elif depth_vertical<depth_horizontal:
                depth=depth_vertical
                color=self.objects[tile_vertical]
                side=1

            #remove fish-eye effect
            depth=depth*(math.cos(self.angle-ray_angle))

            #projection
            projection_height=self.screen_distance/(depth+0.000001)

            #draw walls
            if side==0:
                pygame.draw.rect(self.root,self.colors[color],(ray*self.scale,(height//2)-projection_height//2,self.scale,projection_height))
            else:
                pygame.draw.rect(self.root,list(map(lambda x:x//2,self.colors[color])),(ray*self.scale,(height//2)-projection_height//2,self.scale,projection_height))
            ray_angle+=self.delta_angle
