import time
import logging
from servo import Servo
from planner import Planner
from canvas import Canvas
from utils import rect_to_polar, polar_to_rect

seg_len = 20
max_speed = 3.0
error = max_speed
width = 200
height = 200

class Robot():
    def __init__(self, width, height, x_init, y_init):
        self.canvas = Canvas(width=width, height=height)
        self.doubles = 0
        self.width = width

        # setup servos with init string lengths
        self.x = x_init
        self.y = y_init
        (l, r) = rect_to_polar(width, self.x, self.y)
        self.left_servo = Servo(l, name='l', max_speed = max_speed, error=error)
        self.right_servo = Servo(r, name='r', max_speed = max_speed, error=error)

        servo_max = self.left_servo.max_speed

        self.planner = Planner(width, height, servo_max, seg_len=seg_len)
        self.pen_up()
       
    def pen_down(self):
        self.pen = True

    def pen_up(self):
        self.pen = False

    def move_to(self, x, y):
        log.info("robot moving to xy %.2f, %.2f" % (x, y))
        # get the moves from the planner
        (l, r) = self.left_servo.get_len(), self.right_servo.get_len()
        moves = self.planner.plan(self.x, self.y, x, y, l, r)

        # run the moves
        for move, count in zip(moves,range(len(moves))):
            log.info("move %d" % count)
            self.left_servo.set_len(move['l'], move['ls'])
            self.right_servo.set_len(move['r'], move['rs'])

            while True:
                self.left_servo.update()
                self.right_servo.update()
                xy = polar_to_rect(self.width, self.left_servo.get_len(),
                    self.right_servo.get_len())
                self.canvas.draw_line(self.pen, xy)
                if not self.left_servo.is_running() and not self.right_servo.is_running():
                    break
                elif self.left_servo.is_running() and not self.right_servo.is_running():
                    log.warning("l double move")
                    self.doubles += 1
                elif self.right_servo.is_running() and not self.left_servo.is_running():
                    log.warning("r double move")
                    self.doubles += 1

            self.canvas.show_move(xy)
        # update x & y
        self.x = xy[0] 
        self.y = xy[1] 
        log.info("robot new xy %.2f, %.2f" % (self.x, self.y))


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

    r = Robot(width, height, width/2, height/2)
    r.move_to(width/4,height/4)
    r.pen_down()
    r.move_to(3*width/4,height/4)
    r.move_to(3*width/4,3*height/4)
    r.move_to(width/4,3*height/4)
    r.move_to(width/4,height/4)
    r.finish()
    log.info("doubles = %d" % r.doubles)

