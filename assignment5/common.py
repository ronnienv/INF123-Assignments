from random import randint
import math

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

    def find_pellet(self):
        closest = self.pellets[0]
        shortest_dist = self.distance((self.mybox[0], self.mybox[1]), (closest[0], closest[1]))
        for pellet in self.pellets:
            current_dist = self.distance((self.mybox[0], self.mybox[1]), (pellet[0], pellet[1]))
            if current_dist < shortest_dist:
                shortest_dist = current_dist
                closest = pellet

        return closest

    def get_pellet(self):
        closest = self.find_pellet()
        best_cmd = 'down'
        shortest_dist = self.distance((self.mybox[0], self.mybox[1]+1), (closest[0], closest[1]))
        for cmd in self.cmd_directions:
            current_dist = self.distance((self.mybox[0] + self.cmd_directions[cmd][0], self.mybox[1] + self.cmd_directions[cmd][1]), (closest[0], closest[1]))
            if current_dist < shortest_dist:
                shortest_dist = current_dist
                best_cmd = cmd

        self.do_cmd(best_cmd)

    def distance(self, p0, p1):
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

            
