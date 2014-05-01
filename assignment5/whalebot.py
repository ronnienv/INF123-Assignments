from random import randint
from time import sleep, clock
import time
import common

################### CONTROLLER #############################

import common

class Controller():
    def __init__(self, m):
        self.m = m
    
    def poll(self):
        #randomly moves the whale every frame
        # cmd_list = ["up","down","left","right"]
        # cmd = cmd_list[randint(0, 3)]

        self.m.get_pellet()

################### VIEW #############################

class View():
    ticks = 0

    def __init__(self, m):
        self.m = m
        
    def display(self):
        self.ticks+=1
        if self.ticks % 50 == 0:
            print "Position: " + str(self.m.mybox[0]) + ", " + str(self.m.mybox[1])
    
################### LOOP #############################

model = common.Model()
c = Controller(model)
v = View(model)

while not model.game_over:
    try:
        sleep(0.02)
        c.poll()
        model.update()
        v.display()
    except KeyboardInterrupt:
        print "****bot terminated***"
        model.game_over = True