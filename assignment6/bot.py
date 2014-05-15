from random import choice, randint
from time import sleep
from network import Handler, poll
from pygame import Rect, init as init_pygame
from pygame.event import get as get_pygame_events
from pygame.draw import rect as draw_rect
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT
from pygame.time import Clock

from network import Handler, poll

import pygame


################### MODEL #############################

def collide_boxes(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return x1 < x2 + w2 and y1 < y2 + h2 and x2 < x1 + w1 and y2 < y1 + h1
    

class Model():
    
    cmd_directions = {'up': (0, -1),
                      'down': (0, 1),
                      'left': (-1, 0),
                      'right': (1, 0)}
    
    def __init__(self):
        self.borders = [[0, 0, 2, 300],
                        [0, 0, 400, 2],
                        [398, 0, 2, 300],
                        [0, 298, 400, 2]]
        self.pellets = [ [randint(10, 380), randint(10, 280), 5, 5] 
                        for _ in range(4) ]
        self.game_over = False
        self.mydir = self.cmd_directions['down']  # start direction: down
        self.mybox = [200, 150, 10, 10]  # start in middle of the screen
        self.got_pellet = False
        self.connected = False
        self.players = {}
        
    def do_cmd(self, cmd):
        if cmd == 'quit':
            self.game_over = True
        else:
            self.mydir = self.cmd_directions[cmd]
            
    def update(self):
        # move me
        self.mybox[0] += self.mydir[0]
        self.mybox[1] += self.mydir[1]
        # potential collision with a border
        for b in self.borders:
            if collide_boxes(self.mybox, b):
                self.mybox = [200, 150, 10, 10]
        # potential collision with a pellet
        for index, pellet in enumerate(self.pellets):
            if collide_boxes(self.mybox, pellet):
                self.mybox[2] *= 1.2
                self.mybox[3] *= 1.2
                self.pellets[index] = [randint(10, 380), randint(10, 280), 5, 5]


################### CONTROLLER #############################

class RandomBotController():
    def __init__(self, m):
        self.m = m
        self.cmds = ['up', 'down', 'left', 'right']
        
    def poll(self):
        self.m.do_cmd(choice(self.cmds))
        
################### CONTROLLER #############################

class SmartBotController():
    def __init__(self, m):
        self.m = m
        
    def poll(self):

        poll()

        p = self.m.pellets[0]  # always target the first pellet
        b = self.m.mybox
        if p[0] > b[0]:
            cmd = 'right'
        elif p[0] < b[0]: # p[2] to avoid stuttering left-right movement
            cmd = 'left'
        elif p[1] > b[1]:
            cmd = 'down'
        else:
            cmd = 'up'
        self.m.do_cmd(cmd)

################### CONTROLLER #############################

def make_rect(quad):  # make a pygame.Rect from a list of 4 integers
    x, y, w, h = quad
    return Rect(x, y, w, h)
    
class Client(Handler):

    def on_open(self):
        global model
        model.connected = True

    def on_close(self):
        global model
        model.connected = False

            
    def on_msg(self, data):
        global model

        model.borders = [make_rect(b) for b in data['borders']]
        pellets = [make_rect(p) for p in data['pellets']]
        model.players = {name: make_rect(p) for name, p in data['players'].items()}
        model.myname = data['myname']
        model.mybox = model.players[model.myname]

        if type(pellets[0]) == type(model.pellets[0]) and model.pellets != pellets:
            for pellet in model.pellets:
                if collide_boxes(pellet, model.mybox):
                    model.got_pellet = True

        model.pellets = pellets

class NetworkController():
    def __init__(self, m):
        self.m = m
        self.client = Client('localhost', 8888)

    def poll(self):
        clock = Clock()

        poll()

        p = self.m.pellets[0]  # always target the first pellet
        b = self.m.mybox
        if p[0] > b[0]:
            cmd = 'right'
        elif p[0] + p[2] - 1< b[0]: # p[2] to avoid stuttering left-right movement
            cmd = 'left'
        elif p[1] > b[1]:
            cmd = 'down'
        else:
            cmd = 'up'

        msg = {'input': cmd}
        self.client.do_send(msg)

        # removes jittery movement
        clock.tick(30)

################### CONSOLE VIEW #############################

class ConsoleView():
    def __init__(self, m):
        self.m = m
        self.frame_freq = 20
        self.frame_count = 0
        
    def display(self):
        self.frame_count += 1
        if self.frame_count == self.frame_freq:
            self.frame_count = 0
            b = self.m.mybox
            print 'Position: %d, %d' % (b[0], b[1])


################### CONSOLE VIEW #############################

class ConsoleBotView():
    def __init__(self, m):
        global model
        self.connected = model.connected
        
    def display(self):
        global model
       
        if model.connected and self.connected == False:
            self.connected = True
            print "*** Connected to Server ***"

        elif model.connected:
            if model.got_pellet:
                print "*** Got Pellet ***"
                model.got_pellet = False
        else:
           print "*** Disconnected From Server ***"
           model.game_over = True 


################### PYGAME VIEW #############################
# this view is only here in case you want to see how the bot behaves


class PygameView():
    
    def __init__(self, m):
        self.m = m
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        
    def display(self):
        pygame.event.pump()
        screen = self.screen
        borders = [pygame.Rect(b[0], b[1], b[2], b[3]) for b in self.m.borders]
        pellets = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in self.m.pellets]
        b = self.m.mybox
        myrect = pygame.Rect(b[0], b[1], b[2], b[3])
        screen.fill((0, 0, 64))  # dark blue
        [draw_rect(screen, (0, 191, 255), b) for b in borders]  # deep sky blue 
        [pygame.draw.rect(screen, (255, 192, 203), p) for p in pellets]  # pink
        [pygame.draw.rect(screen, (0, 191, 255), b) for b in borders]  # red
        pygame.display.update()

################### CLIENT SERVER PYGAME VIEW #############################

class ClientServerPygameView():
    
    def __init__(self, m):
        self.m = m
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        
    def display(self):
        pygame.event.pump()
        screen = self.screen
        borders = [pygame.Rect(b[0], b[1], b[2], b[3]) for b in self.m.borders]
        pellets = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in self.m.pellets]
        b = self.m.mybox
        myrect = pygame.Rect(b[0], b[1], b[2], b[3])
        screen.fill((0, 0, 64))  # dark blue

        for player in self.m.players.items():
            name = player[0]
            if name != self.m.myname:
                draw_rect(screen, (255, 0, 0), player[1])  # red
            else:
                draw_rect(screen, (0, 191, 255), player[1])  # deep sky blue

        [pygame.draw.rect(screen, (255, 192, 203), p) for p in pellets]  # pink
        [pygame.draw.rect(screen, (0, 191, 255), b) for b in borders]  # red
        pygame.display.update()
        
        
################### LOOP #############################

model = Model()
# c = SmartBotController(model)
c = NetworkController(model)
# v = ConsoleView(model)
# v2 = PygameView(model)
v3 = ConsoleBotView(model)
# v4 = ClientServerPygameView(model)

while not model.game_over:
    sleep(0.02)
    c.poll()
    model.update()
    # v.display()
    # v2.display()
    v3.display()
    # v4.display()