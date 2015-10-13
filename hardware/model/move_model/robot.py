import time
import random
import logging
from servo import Servo
from ppath import Moves
from canvas import Canvas
from utils import rect_to_polar, polar_to_rect
import argparse

conf = {
    'plan_len' : 10,    # cm
    'max_spd' : 1.0,
    'min_spd' : 1.0,
    'spd_err' : 0.0,  # % error in speed measurement of servo
    'acc' : 0.1,
    'len_err' : 0,   # random length err up to this in cm
    'width' : 700,
    'height' : 500,
    'scaling' : 8, # how much bigger to make the png than the robot
}

class Robot():
    def __init__(self, width, height, x_init, y_init):
        self.canvas = Canvas(conf)
        self.doubles = 0
        self.width = width
        self.moves = Moves(conf, x_init, y_init)

        # setup servos with init string lengths
        self.x = x_init
        self.y = y_init
        
        log.info("robot starting at x=%.2f y=%.2f" % (x_init, y_init))
        (l, r) = rect_to_polar(width, self.x, self.y)

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
        self.moves.output()

        
        """
        log.info("robot moving to xy %.2f, %.2f" % (x, y))
        # random error to simulate what happens when length is not measured
        # should be done in servo, but hard to do because path is split
        x += random.random() * conf['len_err']
        y += random.random() * conf['len_err']

        # get the moves from the planner
        (l, r) = self.left_servo.get_len(), self.right_servo.get_len()
        (target_l, target_r) = rect_to_polar(self.width, x, y)
        moves = self.planner.plan(self.x, self.y, x, y, l, r)
        # accelerate if possible
        moves = self.planner.accel(moves)

        # run the moves
        count = 0
        for move, count in zip(moves,range(len(moves))):
            log.debug("move %d" % count)
            self.left_servo.set_len(move['l'], move['ls'])
            self.right_servo.set_len(move['r'], move['rs'])

            while True:
                self.left_servo.update()
                self.right_servo.update()
                count += 1
                if not self.left_servo.is_running() and not self.right_servo.is_running():
                    break
                elif self.left_servo.is_running() and not self.right_servo.is_running():
                    log.debug("l double move")
                    self.doubles += 1
                elif self.right_servo.is_running() and not self.left_servo.is_running():
                    log.debug("r double move")
                    self.doubles += 1

            speed = self.calculate_speed(move)
            log.info("speed = %.2f" % speed)
            xy = polar_to_rect(self.width, self.left_servo.get_len(), self.right_servo.get_len())
            self.canvas.draw_line(self.pen, xy, speed)
            self.canvas.show_move(xy)

        # update x & y
        self.canvas.show_move(xy,type='seg')
        self.x = xy[0] 
        self.y = xy[1] 
        log.info("robot new xy %.2f, %.2f" % (self.x, self.y))
        log.info("servos updated l=%d, r=%d" % (self.left_servo.updates, self.right_servo.updates))
        self.l_error += abs(self.left_servo.get_len() - target_l)
        self.r_error += abs(self.right_servo.get_len() - target_r)
        log.info("len errors l=%.2f, r=%.2f" % (self.l_error, self.r_error))
        log.info("servos top speed l=%.2f, r=%.2f" % (self.left_servo.max_spd, self.right_servo.max_spd))
        """

    def finish(self):
        self.canvas.save()

if __name__ == '__main__':

    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
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

