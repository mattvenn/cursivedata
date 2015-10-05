import time
import logging
from servo import Servo
from planner import Planner
from canvas import Canvas


class Robot():
    def __init__(self, width=100, height=100):
        self.canvas = Canvas(width=width, height=height)
        self.width = width

        # setup servos with init string lengths
        self.x = width/2
        self.y = height/4
        self.planner = Planner(width, height)
        (l, r) = self.planner.rect_to_polar(self.x, self.y)

        self.left_servo = Servo(l)
        self.right_servo = Servo(r)
        self.pen_up()
       
    def pen_down(self):
        self.pen = True

    def pen_up(self):
        self.pen = False

    def move_to(self, x, y):
        # get the moves from the planner
        moves = self.planner.plan(self.x, self.y, x, y)

        # run the moves
        for move in moves:
            self.left_servo.set_len(move['l'], move['ls'])
            self.right_servo.set_len(move['r'], move['rs'])

            while self.left_servo.is_running() or self.right_servo.is_running():
                self.left_servo.update()
                self.right_servo.update()
                xy = self.planner.polar_to_rect(self.left_servo.get_len(),
                    self.right_servo.get_len())
                self.canvas.update(self.pen, xy)
        # update x & y
        self.x = xy[0] 
        self.y = xy[1] 


    def finish(self):
        self.canvas.save()

if __name__ == '__main__':

    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    r = Robot()
    r.move_to(25,25)
    r.pen_down()
    r.move_to(75,25)
    r.move_to(75,75)
    r.move_to(25,75)
    r.move_to(25,25)
    r.finish()

