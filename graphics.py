import math
import pygame
width,height=1200,600
MAP=[
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
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1]
]

coords=[1.5,1.5] 
angle=0 # initial angle (starts from east)
fov=math.pi/3 # field of view
max_depth=10 # ray depth
number_of_rays=width # resolution / number of rays
delta_angle=fov/number_of_rays # angle between each ray

scale=width//number_of_rays # again, a factor of resolution

screen_distance=(width/2)/math.tan(fov/2) # screen distance

move=0.060 # step size
rotate=10  # rotation step

objects={} # objects tuple, later keeps the walls location
colors={1:(255,0,0),2:(0,0,255),3:(0,255,0),4:(255,0,255)} # 1: red, 3: green


def setup_map(root):
    for i in range(len(MAP)):
        for j in range(len(MAP[i])):
            if MAP[i][j]:
                objects[(j,i)]=MAP[i][j]
    pygame.draw.rect(root,(50,50,50),(0,height//2,width,height)) # default background
    pygame.draw.rect(root,(30,30,30),(0,0,width,height//2)) # default background

def movements(root):
    global angle
    mx=move*math.cos(angle)
    my=move*math.sin(angle)
    dx,dy=0,0

    pressed=pygame.key.get_pressed() # controlls 
    if pressed[pygame.K_w]:
        print(pygame.surfarray.array3d(root))
        dx+=mx
        dy+=my
    if pressed[pygame.K_s]:
        dx+=-mx
        dy+=-my
    if pressed[pygame.K_a]:
        angle+=-rotate*0.002
    if pressed[pygame.K_d]:
        angle+=rotate*0.002

    if (int(coords[0]+dx),int(coords[1])) not in objects: # do not update coords if I am heading into a wall
        coords[0]+=dx
    if (int(coords[0]),int(coords[1]+dy)) not in objects:
        coords[1]+=dy
    if MAP[int(coords[1])][int(coords[0]+dx)] == 3: # do not update coords if I am heading into a wall
        objects.pop((int(coords[0]+dx),int(coords[1])))
        MAP[int(coords[1])][int(coords[0]+dx)] = 0
    if MAP[int(coords[1]+dy)][int(coords[0])] == 3:
        objects.pop((int(coords[0]),int(coords[1]+dy)))
        MAP[int(coords[1]+dy)][int(coords[0])] = 0

def raycast(root):
    ray_angle=(angle-(fov/2))+0.000001 # error never makes this zero
    color=0 

    for ray in range(number_of_rays):

        sin_angle=math.sin(ray_angle)
        cos_angle=math.cos(ray_angle)

        #vertical
        x_vertical,dx=(int(coords[0])+1,1) if cos_angle>0 else (int(coords[0])-0.000001,-1)
        depth_vertical=(x_vertical-coords[0])/cos_angle

        y_vertical=(depth_vertical*sin_angle)+coords[1]

        delta_depth=dx/cos_angle
        dy=delta_depth*sin_angle

        for i in range(max_depth):
            tile_vertical=(int(x_vertical),int(y_vertical))
            if tile_vertical in objects:
                break
            x_vertical+=dx
            y_vertical+=dy
            depth_vertical+=delta_depth

        #horizontal
        y_horizontal,dy=(int(coords[1])+1,1) if sin_angle>0 else (int(coords[1])-0.000001,-1)
        depth_horizontal=(y_horizontal-coords[1])/sin_angle

        x_horizontal=(depth_horizontal*cos_angle)+coords[0]

        delta_depth=dy/sin_angle
        dx=delta_depth*cos_angle

        for i in range(max_depth):
            tile_horizontal=(int(x_horizontal),int(y_horizontal))
            if tile_horizontal in objects:
                break
            x_horizontal+=dx
            y_horizontal+=dy
            depth_horizontal+=delta_depth

        if depth_horizontal<depth_vertical:
            depth=depth_horizontal
            color=objects[tile_horizontal]
            side=0
        elif depth_vertical<depth_horizontal:
            depth=depth_vertical
            color=objects[tile_vertical]
            side=1

        #remove fish-eye effect
        depth=depth*(math.cos(angle-ray_angle))

        #projection
        projection_height=screen_distance/(depth+0.000001)

        #draw walls
        if side==0:
            pygame.draw.rect(root,colors[color],(ray*scale,(height//2)-projection_height//2,scale,projection_height))
        else:
            pygame.draw.rect(root,list(map(lambda x:x//2,colors[color])),(ray*scale,(height//2)-projection_height//2,scale,projection_height))
        ray_angle+=delta_angle