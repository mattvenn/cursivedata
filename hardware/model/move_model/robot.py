#!/usr/bin/env python
import sys
import time
import random
import logging
from servo import Servo
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
        self.moves = Moves(x_init, y_init)

        # setup servos with init string lengths
        self.x = x_init
        self.y = y_init
        
        log.info("robot starting at x=%.2f y=%.2f" % (x_init, y_init))
        (l, r) = rect_to_polar(self.x, self.y)

        self.left_servo = Servo(conf, l, name='l')
        self.right_servo = Servo(conf, r, name='r')
        self.l_error = 0
        self.r_error = 0

        self.pen_up()
        
       
    def pen_down(self):
        self.pen = True

    def pen_up(self):
        self.pen = False

    # add the moves to the list
    def add_point(self, x, y):
        #move = { 'x1': x, 'y1': y, 'pen' : self.pen }
        self.moves.add_point(x,y)
    
    # do the drawing
    def start(self):
        self.moves.process()
        moves = self.moves.output()

        log.info("drawing")
        
        # run the moves
        count = 0
        for step, count in zip(moves,range(len(moves))):
            log.info("step %03d: moveto x=%.2f, y=%.2f, targ spd=%.2f, l=%.2f @ %.2f, r=%.2f @ %.2f" % (count, step['x'], step['y'], step['targ_spd'], step['l'], step['l_targ_spd'], step['r'], step['r_targ_spd']))

            self.left_servo.set_len(step['l'], step['l_targ_spd'])
            self.right_servo.set_len(step['r'], step['r_targ_spd'])

            while True:
                self.left_servo.update()
                self.right_servo.update()
                count += 1
                if self.left_servo.finished() and self.right_servo.finished():
                    break

            xy = polar_to_rect(self.left_servo.get_len(), self.right_servo.get_len())
            self.canvas.draw_line(self.pen, xy, step['targ_spd'])
            self.canvas.show_move(xy)
            self.left_servo.log_error()
            self.right_servo.log_error()

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
    rob.start()
    rob.finish()
    log.info("doubles = %d" % rob.doubles)

