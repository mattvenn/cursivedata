#!/usr/bin/env python
from pprint import pprint
import sys
import numpy as np
import time
import random
import logging
from ppath import Moves
from canvas import Canvas
from utils import rect_to_polar, polar_to_rect
from conf import conf
import argparse


class Robot():
    def __init__(self, width, height, x_init, y_init):
        self.canvas = Canvas(conf)
        self.doubles = 0
        self.width = width
        self.moves = Moves()

        # setup servos with init string lengths
        self.x = x_init
        self.y = y_init
        
        log.info("robot starting at x=%.2f y=%.2f" % (x_init, y_init))
        (l, r) = rect_to_polar(self.x, self.y)

#        self.left_servo = Servo(len=l, name='l')
#        self.right_servo = Servo(len=r, name='r')
        self.l_error = 0
        self.r_error = 0

        self.pen_up()
        
       
    def pen_down(self):
        self.pen = True

    def pen_up(self):
        self.pen = False

    # add the moves to the list
    def add_point(self, x, y):
        self.moves.add_point(x, y)
   
    def process(self):
        self.moves.break_segments()
        self.moves.calc_max_velocity()
        self.moves.plan_velocity()
        self.moves.calc_point_times()
        self.moves.interpolate_pos_by_time()
        self.moves.dump()

    # do the drawing
    def start(self):
        moves = self.moves.output()

        log.info("drawing")
        
        # run the moves
        count = 0
        for step, count in zip(moves,range(len(moves))):
            #log.info("step %03d: moveto x=%.2f, y=%.2f, targ spd=%.2f, l=%.2f @ %.2f, r=%.2f @ %.2f" % (count, step['x'], step['y'], step['targ_spd'], step['l'], step['l_targ_spd'], step['r'], step['r_targ_spd']))
            log.info("step %03d: l=%.2f r=%.2f" % (count, step['l'], step['r']))

            #self.left_servo.set_len(step['l'])
            #self.right_servo.set_len(step['r'])

            xy = polar_to_rect(step['l'], step['r'])
            self.canvas.draw_line(self.pen, xy)
            self.canvas.show_move(xy)

        # update x & y
        self.canvas.show_move(xy,type='seg')
        self.x = xy[0] 
        self.y = xy[1] 
        log.info("robot new xy %.2f, %.2f" % (self.x, self.y))
        log.info("servos updated l=%d, r=%d" % (self.left_servo.updates, self.right_servo.updates))

    def finish(self):
        self.canvas.save()

if __name__ == '__main__':

    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(name)-10s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    width = conf['width']
    height = conf['height']
    rob = Robot(width, height, width/2, height/2)

    parser = argparse.ArgumentParser(description="feed polar files to polargraph robot")
    parser.add_argument('--file', required=True, action='store', dest='file', help="file to open")
    args = parser.parse_args()


    with open(args.file) as fh:
    #with open("circle.polar") as fh:
        for line in fh.readlines():
            if line.startswith('d'):
                if '0' in line:
                    rob.pen_up()
                else:
                    rob.pen_down()
            elif line.startswith('g'):
                line = line.lstrip('g')
                l, r = line.split(',')
                rob.add_point(float(l),float(r))

    """
    rob.move_to(width/4,height/4)
    rob.pen_down()
    rob.move_to(3*width/4,height/4)
#    rob.move_to(3*width/4,3*height/4)
#    rob.move_to(width/4,3*height/4)
#    rob.move_to(width/4,height/4)



    steps = 5 
    step = width/2 / steps
    for i in range(steps+1):
        r.move_to(width/4+step*i,height/4)
        r.move_to(width/4+step*i,3*height/4)
    """
    rob.process()
#    rob.start()
#    rob.finish()
    log.info("doubles = %d" % rob.doubles)

