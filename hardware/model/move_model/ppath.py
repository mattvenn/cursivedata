import math
import logging
from utils import *
from segment import Segment

log = logging.getLogger(__name__)

# TODO merge moves and path
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
            log.debug("segment %d" % count)
            count += 1
            s.calculate_lengths()

        # rectangular velocity planning
        log.info("velocity planning")
        count = 0
        for s in self.path.segments:
            log.debug("segment %d" % count)
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

    #TODO, probably needs to take into acount:
        * max servo speeds
        * max servo acc/dec
    #TODO
        still got an out by one bug somewhere, polar speeds are off in relation to linear speeds
    """ 
    def calculate_string_speeds(self):
        last_step = None
        count = 0
        timestamp = 0
        for step in self.steps:
            step['l'],step['r'] = rect_to_polar(step['x'], step['y'])
            step['l_targ_spd'] = 0
            step['r_targ_spd'] = 0

            if last_step is None:
                last_step = step
                continue
#            if count == 106:
#                import ipdb; ipdb.set_trace()
            
            dl = step['l'] - last_step['l']
            dr = step['r'] - last_step['r']
            last_step['l_targ_spd'] = last_step['targ_spd'] * dl
            last_step['r_targ_spd'] = last_step['targ_spd'] * dr
            log.debug("step %d: l=%.2f @ %.2f, r=%.2f @ %.2f" % (count, step['l'], step['l_targ_spd'], step['r'], step['r_targ_spd']))

            last_step = step
            count += 1
            
        
    def output(self):
        log.info("dumping commands")
        count = 0
        for step in self.steps:
            log.info("step %03d: moveto x=%.2f, y=%.2f, targ spd=%.2f, l=%.2f @ %.2f, r=%.2f @ %.2f" % (count, step['x'], step['y'], step['targ_spd'], step['l'], step['l_targ_spd'], step['r'], step['r_targ_spd']))
            count += 1
        # open a file and dump the steps

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

