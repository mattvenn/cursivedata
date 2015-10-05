import time
import logging
from servo import Servo
from canvas import Canvas
import threading
import math


class Robot():
    def __init__(self, width=100, height=100):
        self.canvas = Canvas(width=width, height=height)
        self.width = width

        # setup servos with init string lengths
        (l, r) = self.rect_to_polar(width/2, height/4)
        self.left_servo = Servo(l)
        self.right_servo = Servo(r)
        self.pen_up()
       
    def pen_down(self):
        self.pen = True

    def pen_up(self):
        self.pen = False

    def move_to(self, x, y):
        # do some validation later
        (l, r) = self.rect_to_polar(x, y)

        self.left_servo.set_len(l)
        self.right_servo.set_len(r)

        while self.left_servo.is_running() or self.right_servo.is_running():
            self.left_servo.update()
            self.right_servo.update()
            xy = self.polar_to_rect(self.left_servo.get_len(),
                self.right_servo.get_len())
            self.canvas.update(self.pen, xy)
        
    def polar_to_rect(self, a, c):
        b = self.width
        i = (a*a+b*b-c*c)/(2.0*a*b)
        x = i * a
        try:
            y = math.sqrt(1.0 - i*i)*a
        except ValueError:
            print("value error")
            y = 0

        return(x,y)

    def rect_to_polar(self,x,y):
        l = math.sqrt(pow(x,2)+pow(y,2))
        r = math.sqrt(pow((self.width-x),2)+pow(y,2))
        return(l,r)

    def finish(self):
        self.canvas.save()

if __name__ == '__main__':

    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
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

