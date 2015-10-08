import time
import random
import logging
from servo import Servo
from planner import Planner
from canvas import Canvas
from utils import rect_to_polar, polar_to_rect

conf = {
    'seg_len' : 10,    # cm
    'max_spd' : 10.0,
    'min_spd' : 0.1,
    'spd_err' : 0.00,  # % error in speed measurement of servo
    'acc' : 5.0,
    'len_err' : 0,   # random length err up to this in cm
    'width' : 200,
    'height' : 200,
    'scaling' : 5, # how much bigger to make the png than the robot
}

class Robot():
    def __init__(self, width, height, x_init, y_init):
        self.canvas = Canvas(conf)
        self.doubles = 0
        self.width = width

        # setup servos with init string lengths
        self.x = x_init
        self.y = y_init
        (l, r) = rect_to_polar(width, self.x, self.y)

        self.left_servo = Servo(conf, l, name='l')
        self.right_servo = Servo(conf, r, name='r')
        self.l_error = 0
        self.r_error = 0

        self.planner = Planner(conf)
        self.pen_up()
       
    def pen_down(self):
        self.pen = True

    def pen_up(self):
        self.pen = False

    def move_to(self, x, y):
        log.info("robot moving to xy %.2f, %.2f" % (x, y))
        # random error to simulate what happens when length is not measured
        # should be done in servo, but hard to do because path is split
        x += random.random() * conf['len_err']
        y += random.random() * conf['len_err']

        # get the moves from the planner
        (l, r) = self.left_servo.get_len(), self.right_servo.get_len()
        (target_l, target_r) = rect_to_polar(self.width, x, y)
        moves = self.planner.plan(self.x, self.y, x, y, l, r)
        # accellerate if possible
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
                xy = polar_to_rect(self.width, self.left_servo.get_len(),
                    self.right_servo.get_len())
                self.canvas.draw_line(self.pen, xy)
                if not self.left_servo.is_running() and not self.right_servo.is_running():
                    break
                elif self.left_servo.is_running() and not self.right_servo.is_running():
                    log.debug("l double move")
                    self.doubles += 1
                elif self.right_servo.is_running() and not self.left_servo.is_running():
                    log.debug("r double move")
                    self.doubles += 1

            self.canvas.show_move(xy)
        # update x & y
        self.x = xy[0] 
        self.y = xy[1] 
        log.info("robot new xy %.2f, %.2f" % (self.x, self.y))
        log.info("servos updated l=%d, r=%d" % (self.left_servo.updates, self.right_servo.updates))
        self.l_error += abs(self.left_servo.get_len() - target_l)
        self.r_error += abs(self.right_servo.get_len() - target_r)
        log.info("len errors l=%.2f, r=%.2f" % (self.l_error, self.r_error))
        log.info("servos top speed l=%.2f, r=%.2f" % (self.left_servo.max_spd, self.right_servo.max_spd))



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
    r = Robot(width, height, width/2, height/2)
#    r.move_to(width/4,height/4)
#    r.pen_down()
#    r.move_to(3*width/4,height/4)
#    r.move_to(3*width/4,3*height/4)
#    r.move_to(width/4,3*height/4)
#    r.move_to(width/4,height/4)
#    r.move_to(3*width/4,height/4)
    steps = 5 
    step = width/2 / steps
    for i in range(steps+1):
        r.move_to(width/4+step*i,height/4)
        r.move_to(width/4+step*i,3*height/4)
    r.finish()
    log.info("doubles = %d" % r.doubles)

