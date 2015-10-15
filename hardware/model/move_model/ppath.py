import math
import logging
from utils import *
from segment import Segment

log = logging.getLogger(__name__)

# contains all the paths
class Moves():
    def __init__(self, x, y):
        self.path = Path()
        self.x = x
        self.y = y
   
    def add_point(self, x, y):
        s = Segment(self.x, self.y, x, y)
        self.x = x
        self.y = y
        log.info("appended segment %s" % s)
        self.path.add_segment(s)
       
    def process(self):
        log.info("split segments")
        count = 0
        for s in self.path.segments:
            log.info("segment %d" % count)
            count += 1
            s.calculate_lengths()

        # rectangular velocity planning
        log.info("velocity planning")
        count = 0
        for s in self.path.segments:
            log.info("segment %d" % count)
            count += 1
            s.calculate_speeds()

        # build list of all steps
        self.steps = []
        for s in self.path.segments:
            self.steps += s.get_steps()
        log.info("route planned in %d steps" % len(self.steps))

        # convert to string velocity
        log.info("rect -> polar")
        self.calculate_string_speeds()

    """
    * iterates over all steps
    * follows rectangular speed profiles
    * calculates string speeds
    """ 
    def calculate_string_speeds(self):
        last_step = None
#        import ipdb; ipdb.set_trace()
        count = 0
        for step in self.steps:
            if last_step is None:
                last_step = step
                continue
            
            dx = step['x'] - last_step['x']
            dy = step['y'] - last_step['y']
            # where are we using the calculated speed?
            step['dl'], step['dr'] = rect_speed_to_polar_speed(
                step['x'], step['y'],
                last_step['x'], last_step['y'])
            log.info("step %d: dl=%.2f, dr=%.2f, end speed %.2f" % (count, step['dl'], step['dr'], step['speed']))

            last_step = step
            count += 1
            
        

    def output(self):
        log.info("dumping commands")

# paths start and stop at 0 speed
class Path():
    def __init__(self):
        self.segments = []

    def add_segment(self, segment):
        # work out speeds
        # depends on difference angle between this segment & previous
        if len(self.segments):
            angle = self.segments[-1].angle(segment)
            speed = self.calculate_speed(angle)
            segment.set_start_speed(speed)
            self.segments[-1].set_end_speed(speed)

        self.segments.append(segment)

    """
    nieve calculation for now
    returns 1 for full speed, 0 for stop

    should be based on a model that takes into account :

    * weight of gondola in y 
    * minimise swing in x
    """
    def calculate_speed(self, angle):
        if angle > 90:
            angle = 90
        speed = 1 - (angle / 90.0)
        return speed

