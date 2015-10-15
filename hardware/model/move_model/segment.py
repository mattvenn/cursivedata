from utils import *
import logging
log = logging.getLogger(__name__)
from conf import conf

# segments are each straight line in a path
class Segment():
    def __init__(self, x1, y1, x2, y2):
        # start and ending speed
        self.s_spd = 0
        self.e_spd = 0
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        (self.l1, self.r1) = rect_to_polar(x1, y1)
        (self.l2, self.r2) = rect_to_polar(x2, y2)
        self.v = [x2 - x1, y2 - y1]

    def set_start_speed(self, speed):
        self.s_spd = speed

    def set_end_speed(self, speed):
        self.e_spd = speed

    def dotproduct(self, vect):
        return sum((a*b) for a, b in zip(self.v, vect.v))

    def length(self):
        return math.sqrt(self.dotproduct(self))

    def angle(self, vect):
        return math.degrees(math.acos(self.dotproduct(vect) / (self.length() * vect.length())))

    def __str__(self):
        return "%.2f,%.2f -> %.2f,%.2f" % (self.x1,self.y1,self.x2,self.y2)


    def get_steps(self):
        return self.step_list

    # break segment down into small enough chunks
    def calculate_lengths(self): 
        # work out steps
        steps = int(self.length() / conf['plan_len'])
        
        # ensure we have at least one step
        if steps == 0:
            steps = 1

        log.info("planning %s" % self)
        log.info("covering distance %.2f in %d steps" % (self.length(), steps))

        # step vector: amount change per step
        self.step_vect = self.v[0] / steps, self.v[1] / steps
        log.info("step vector=%.2f,%.2f" % (self.step_vect[0], self.step_vect[1]))

        # store all the steps
        self.step_list = []

        # for each step
        for step in range(1,steps+1):
            # calculate new target
            xstep = self.x1 + self.step_vect[0] * step
            ystep = self.y1 + self.step_vect[1] * step
            self.step_list.append({'x': xstep, 'y': ystep, 'length': self.length() / steps })


    """
    * iterates over all steps
    * creates a speed profile over the steps that is in keeping with defined start, stop and max speeds
    * speed is rectangular, NOT string speeds

    informed by linux cnc: http://wiki.linuxcnc.org/cgi-bin/wiki.pl?Simple_Tp_Notes

    probably need to make not dependent on number of steps, or at least ensure that segments don't have 0 speeds all the way through
    """
    def calculate_speeds(self):
        steps = len(self.step_list)
        # y = mx + c
        m_end = -conf['acc']
        m_start = conf['acc']
        c_end = self.e_spd + steps * conf['acc']
        c_start = self.s_spd
        count = 1
        for step in self.step_list:
            # start with highest velocity that can satisfy end
            v_suggest = m_end * count + c_end

            # clamp to max speed
            if v_suggest > conf['max_spd']:
                v_suggest = conf['max_spd']

            # check satisfies acceleration at start
            v_max = m_start * count + c_start
            if v_suggest > v_max:
                v_suggest = v_max

            # the rect speed we aim to achieve at the end of the segment
            step['targ_spd'] = v_suggest
            log.info("step=%d speed=%.2f" % (count, step['targ_spd']))
            count += 1

        
