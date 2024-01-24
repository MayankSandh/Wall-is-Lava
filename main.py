import pygame
from graphics import setup_map, raycast, movements
pygame.init()

width,height=1200,600
root=pygame.display.set_mode((width,height))
pygame.mouse.set_visible(False)


gameover=False
clock=pygame.time.Clock()

def fetch_game_state():
    game_state = pygame.surfarray.array3d(root)
    return game_state
def perform_action(action):
    pass

while not gameover:
    root.fill('black')
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            gameover=True
        if i.type == pygame.KEYUP:
            if i.key==pygame.K_q:
                gameover=True

    setup_map(root)
    raycast(root)
    movements()

    pygame.display.set_caption(str(clock.get_fps()//1))

    clock.tick(60)
    pygame.display.update()
