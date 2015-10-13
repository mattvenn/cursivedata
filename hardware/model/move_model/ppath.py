import math
import logging
from utils import *
from segment import Segment

log = logging.getLogger(__name__)

# contains all the paths
class Moves():
    def __init__(self, conf, x, y):
        self.conf = conf
        self.path = Path(conf)
        self.x = x
        self.y = y
   
    def add_point(self, x, y):
        s = Segment(self.conf, self.x, self.y, x, y)
        self.x = x
        self.y = y
        log.info("appended segment %s" % s)
        self.path.add_segment(s)
       
    def process(self):
        log.info("processing path")
        for s in self.path.segments:
            s.calculate_lengths()

        for s in self.path.segments:
            s.calculate_speeds()

    def output(self):
        log.info("dumping commands")
        for s in self.path.segments:
            s.log_steps()

# paths start and stop at 0 speed
class Path():
    def __init__(self, conf):
        self.segments = []
        self.conf = conf

    def add_segment(self, segment):
        # work out speeds
        # depends on difference angle between this segment & previous
        if len(self.segments):
            angle = self.segments[-1].angle(segment)
            speed = self.calculate_speed(angle)
            segment.set_start_speed(speed)
            self.segments[-1].set_end_speed(speed)

        self.segments.append(segment)

    # nieve calculation for now
    # returns 1 for full speed, 0 for stop
    def calculate_speed(self, angle):
        if angle > 90:
            angle = 90
        speed = 1 - (angle / 90.0)
        return speed

