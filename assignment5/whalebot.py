from random import randint
from time import sleep, clock
import time
import common

################### CONTROLLER #############################

import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT
import common

class Controller():
    def __init__(self, m):
        self.m = m
    
    def poll(self):
        #randomly moves the whale every frame
        # cmd_list = ["up","down","left","right"]
        # cmd = cmd_list[randint(0, 3)]

        for event in pygame.event.get(): 
            if event.type == QUIT:
                cmd = 'quit'
                self.m.do_cmd(cmd)
            if event.type == KEYDOWN:
                key = event.key
                if key == K_ESCAPE:
                    cmd = 'quit'
                    self.m.do_cmd(cmd)
                    
        self.m.get_pellet()

################### VIEW #############################

class View():
    ticks = 0

    def __init__(self, m):
        self.m = m
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        
    def display(self):
        screen = self.screen
        borders = [pygame.Rect(b[0], b[1], b[2], b[3]) for b in self.m.borders]
        pellets = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in self.m.pellets]
        b = self.m.mybox
        myrect = pygame.Rect(b[0], b[1], b[2], b[3])
        screen.fill((0, 0, 64))  # dark blue
        pygame.draw.rect(screen, (0, 191, 255), myrect)  # Deep Sky Blue
        [pygame.draw.rect(screen, (255, 192, 203), p) for p in pellets]  # pink
        [pygame.draw.rect(screen, (0, 191, 255), b) for b in borders]  # red
        pygame.display.update()

        self.ticks+=1
        if self.ticks % 50 == 0:
            print "Position: " + str(myrect.x) + ", " + str(myrect.y)
    
################### LOOP #############################

model = common.Model()
c = Controller(model)
v = View(model)

while not model.game_over:
    sleep(0.02)
    c.poll()
    model.update()
    v.display()