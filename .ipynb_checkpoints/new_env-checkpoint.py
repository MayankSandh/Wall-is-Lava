import gym
from gym import spaces
import numpy as np
import math
from copy import deepcopy
import pygame

width,height=1200,600

def color_ratio(data, color):
    color_mask = np.all(data == color, axis=-1)
    percentage = (np.sum(color_mask) / np.prod(color_mask.shape)) * 100


class CustomEnv(gym.Env):
    def __init__(self):
        super(CustomEnv, self).__init__()
        self.render_mode = None
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=255, shape=(height, width, 3), dtype=np.float32)

        self.done = False

        """
        if guy dead:
            self.done = True
        """



    def step(self, action):
        self.action = action

        game_state = pygame.surfarray.array3d(self.root)
        self.observation = np.array(game_state, dtype=np.float32)

        self.reward = 0
        self.score = 0
        self.prev_score = 0
        self.time_passed = 0
        # self.time_limit = 60

        # If I account for character death
        if self.done:
            reward_a = -100
        else:
            reward_a = 0

        GREEN = [0,255,0]
        GREEN_LOW = [0,127,0]
        RED = [255, 0, 0]
        RED_LOW = [127, 0, 0]

        green_ratio = color_ratio(game_state, GREEN) + color_ratio(game_state, GREEN_LOW)
        red_ratio = color_ratio(game_state, RED) + color_ratio(game_state, RED_LOW)
        # touching green walls

        # negative award for red walls intensity
        self.reward -= red_ratio/10
        # positive wall for green wall intensity
        self.reward += green_ratio

        self.info = {}
        if self.render_mode == 'human':
            self.render()
        return self.observation, self.reward, self.done, self.info
    
    def reset(self, action):
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
        
        
        game_state = pygame.surfarray.array3d(self.root)
        self.observation = np.array(game_state, dtype=np.
        float32)
        if self.render_mode == 'human':
            self.render()
        return self.observation

    def render(self, render_mode = 'human'):
            self.root.fill('black')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameover = True

            self.setup_map()
            self.raycast()
            self.perform_action()


            pygame.display.set_caption(str(self.clock.get_fps() // 1))

            self.clock.tick(60)
            pygame.display.update()

            """
            if game ded:
                sleep for (0.5 seconds)"""

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
    def perform_action(self):
        mx = self.move * math.cos(self.angle)
        my = self.move * math.sin(self.angle)
        dx, dy = 0, 0

        if self.action == 0:
            dx += mx
            dy += my
        if self.action == 1:
            dx += -mx
            dy += -my
        if self.action == 2:
            self.angle += -self.rotate * 0.002
        if self.action == 3:
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

    def close(self):
        pygame.quit()
