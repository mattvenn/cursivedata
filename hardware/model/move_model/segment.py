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


    def log_steps(self):
        return
        for step in self.step_list:
            log.info("l=%.2f at %.2f, r=%.2f at %.2f" % (step['l'], step['ls'], step['r'], step['rs']))

    # break down into small chunks and calculate string lengths and servo speed ratios
    def calculate_lengths(self): 
        log.info("start speed (rect) <= %.2f%% end speed <= %.2f%%" % (self.s_spd * 100, self.e_spd * 100))
        # work out steps
        steps = int(self.length() / self.conf['plan_len'])
        
        # keep steps even to make acceleration easier
        if steps % 2 != 0:
            steps += 1
        if steps == 0:
            steps = 2
        log.info("planning %s" % self)
        log.info("covering distance %.2f in %d steps" % (self.length(), steps))
        # step vector: amount change per step
        step_vect = self.v[0] / steps, self.v[1] / steps
        speed_step = (self.e_spd - self.s_spd) / steps
        log.info("step vector=%.2f,%.2f speed step=%.2f" % (step_vect[0], step_vect[1], speed_step))

        # store all the steps
        self.step_list = []

        (l, r) = rect_to_polar(self.conf['width'], self.x1, self.y1)
        last_speed = self.s_spd

        # for each step
        for step in range(1,steps+1):
            # calculate new target
            xstep = self.x1 + step_vect[0] * step
            ystep = self.y1 + step_vect[1] * step
            speed = self.s_spd + speed_step * step

            # calculate new string lengths
            (newl, newr) = rect_to_polar(self.conf['width'], xstep, ystep)
            ratio = (newl-l)/(newr-r)
            log.info("ldiff=%.2f rdiff=%.2f ratio=%.2f" % (newl-l, newr-r, ratio) )
            self.step_list.append({ 'l': newl, 'r': newr})

            # set the new x and y
            l = newl
            r = newr
            last_speed = speed


    """
    * iterates over all steps
    * creates a speed profile over the steps that is in keeping with defined start, stop and max speeds
    """
    def calculate_speeds(self):
        steps = len(self.step_list)
        step = 0
        spd = 
        spd_hist = []

        for step in self.step_list:
            if step < steps/2:
                acc = acc + self.conf['acc']
                # limit speed
                if acc >= 1
                    acc = 1
                acc_hist.append(acc)
                acc = new_acc

            step += 1

        return moves
