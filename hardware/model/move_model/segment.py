from utils import *
import logging
log = logging.getLogger(__name__)

# segments are each straight line in a path
class Segment():
    def __init__(self, conf, x1, y1, x2, y2):
        self.conf = conf
        # start and ending speed
        self.s_spd = 0
        self.e_spd = 0
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        (self.l1, self.r1) = rect_to_polar(self.conf['width'], x1, y1)
        (self.l2, self.r2) = rect_to_polar(self.conf['width'], x2, y2)
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

    # break down into small chunks and calculate string lengths and servo speed ratios
    def calculate_lengths(self): 
        log.info("start speed (rect) <= %.2f%% end speed <= %.2f%%" % (self.s_spd * 100, self.e_spd * 100))
        # work out steps
        steps = int(self.length() / self.conf['plan_len'])
        
        # ensure we have at least one step
        if steps == 0:
            steps = 1

        log.info("planning %s" % self)
        log.info("covering distance %.2f in %d steps" % (self.length(), steps))
        # step vector: amount change per step
        self.step_vect = self.v[0] / steps, self.v[1] / steps
        speed_step = (self.e_spd - self.s_spd) / steps
        log.info("step vector=%.2f,%.2f speed step=%.2f" % (self.step_vect[0], self.step_vect[1], speed_step))

        # store all the steps
        self.step_list = []

        (l, r) = rect_to_polar(self.conf['width'], self.x1, self.y1)
        last_speed = self.s_spd

        # for each step
        for step in range(1,steps+1):
            # calculate new target
            xstep = self.x1 + self.step_vect[0] * step
            ystep = self.y1 + self.step_vect[1] * step
            speed = self.s_spd + speed_step * step

            # calculate new string lengths
            (newl, newr) = rect_to_polar(self.conf['width'], xstep, ystep)
            ratio = (newl-l)/(newr-r)
            log.info("ldiff=%.2f rdiff=%.2f ratio=%.2f" % (newl-l, newr-r, ratio) )
            self.step_list.append({ 'l': newl, 'r': newr })

            # set the new x and y
            l = newl
            r = newr
            last_speed = speed


    """
    * iterates over all steps
    * creates a speed profile over the steps that is in keeping with defined start, stop and max speeds
    """
    def calculate_speeds(self):
        # http://wiki.linuxcnc.org/cgi-bin/wiki.pl?Simple_Tp_Notes
        steps = len(self.step_list) - 1
        # y = mx + c
        m_end = -self.conf['acc']
        m_start = self.conf['acc']
        c_end = self.e_spd + steps * self.conf['acc']
        c_start = self.s_spd
        count = 0

        for step in self.step_list:
            # start with highest velocity that can satisfy end
            v_suggest = m_end * count + c_end

            # clamp to max speed
            if v_suggest > self.conf['max_spd']:
                v_suggest = self.conf['max_spd']

            # check satisfies acceleration at start
            v_max = m_start * count + c_start
            if v_suggest > v_max:
                v_suggest = v_max

            step['speed'] = v_suggest
            log.info("step=%d speed=%d" % (count, step['speed']))
            count += 1

        
