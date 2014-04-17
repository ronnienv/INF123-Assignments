"""
Style: main and subroutines
Components: main program and subroutines
Connectors: procedure calls
Constraints: components can't communicate using shared memory (e.g. global 
variables) 
Gains: change the implementation of a subroutine without affecting the main 
program.  
"""

from random import randint

import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT


############################################################

def process_input(prev_direction, paused, paused_dir):
    game_status, direction = 1, prev_direction
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 0 # 0 for game over, 1 for play
        if event.type == KEYDOWN:
            key = event.key
            if key == K_ESCAPE:
                game_status = 0
            elif paused:
                if key == pygame.K_SPACE: 
                    direction = paused_dir
                    paused = False
                else:
                    direction = (0, 0)
            elif key == pygame.K_w:
                direction = (0, -2)
            elif key == pygame.K_s:
                direction = (0, 2)
            elif key == pygame.K_a:
                direction = (-2, 0)
            elif key == pygame.K_d:
                direction = (2, 0)
            elif key == pygame.K_SPACE and paused == False: 
                direction = (0, 0)
                paused = True
    return game_status, direction, paused

############################################################

def draw_everything(screen, mybox, pellets, borders):
    screen.fill((255, 255, 255))  # white
    [pygame.draw.rect(screen, (0, 0, 0), b) for b in borders]  # black
    [pygame.draw.rect(screen, (100, 192, 40), p) for p in pellets]  # puke-green
    pygame.draw.rect(screen, (200, 0, 0), mybox)  # red
    pygame.display.update()

############################################################

def create_box(dims):
    w, h = dims
    box = pygame.Rect(w / 2, h / 2, 10, 10)  # start in middle of the screen
    direction = 0, 1  # start direction: down
    return box, direction

############################################################

def collide(box, boxes):
    # return True if box collides with any entity in boxes
    return box.collidelist(boxes) != -1
    
############################################################

def move(box, direction): 
    return box.move(direction[0], direction[1]) 

############################################################

def create_borders(dims, thickness=2):
    w, h = dims
    return [pygame.Rect(0, 0, thickness, h),
            pygame.Rect(0, 0, w, thickness),
            pygame.Rect(w - thickness, 0, thickness, h),
            pygame.Rect(0, h - thickness, w, thickness),
            pygame.Rect(220, 180, 60, thickness),
            pygame.Rect(150, 100, thickness, 90)]
    
############################################################

def create_pellet(dims, offset):
    w, h = dims
    return pygame.Rect(randint(offset, w - offset),
                       randint(offset, h - offset), 5, 5)

def create_pellets(dims, qty, offset=10): 
    # this is the only subroutine independent of Pygame
    return [create_pellet(dims, offset) for _ in range(qty)]
    
def eat_and_replace_colliding_pellet(box, pellets, dims, offset=10):
    p_index = box.collidelist(pellets)
    if p_index != -1:  # ate a pellet: grow, and replace a pellet
        pellets[p_index] = create_pellet(dims, offset)
        box.size = box.width * 1.2, box.height * 1.2
    return box, pellets
    
############################################################

pygame.init()
clock = pygame.time.Clock()

# display
dims = 400, 300
screen = pygame.display.set_mode(dims)

# game objects
borders = create_borders(dims)
pellets = create_pellets(dims, 4)
mybox, direction = create_box(dims)

# game loop
game_status = 1  # 0 for game over, 1 for play
paused = False
paused_dir = direction
while game_status:

    if paused == False:
        paused_dir = direction

    game_status, direction, paused = process_input(direction, paused, paused_dir)
    
    mybox = move(mybox, direction)
    if collide(mybox, borders):
        mybox, direction = create_box(dims)
    mybox, pellets = eat_and_replace_colliding_pellet(mybox, pellets, dims)
    
    draw_everything(screen, mybox, pellets, borders)
    
    clock.tick(50)  # or sleep(.02) to have the loop Pygame-independent