from math import sqrt, pow
import numpy as np
import logging
from utils import *
from segment import Segment
import pickle

log = logging.getLogger(__name__)

# contains all the paths
class Moves():
    def __init__(self):
        self.points = []
  
    def dump(self):
        with open('points.d', 'w') as fh:
            pickle.dump({'p' : self.points, 'bp': self.broken_points }, fh)
        
    def add_point(self, x, y):
        point = np.array([x,y],dtype=np.float)
        log.info("appending point %s" % (point))
        self.points.append({'point': point})
     
    def break_segments(self):
        self.broken_points = []
        # start from second point
        for p in range(1, len(self.points)):
            log.debug("breaking point %d", p)
            self.break_segment(p)
        # add last point
        self.broken_points.append(self.points[-1])

    # break segment down into small enough chunks
    def break_segment(self, p): 
        # work out steps
        prev_point = self.points[p-1]['point']
        point = self.points[p]['point']
        length = np.linalg.norm(point - prev_point)
        steps = int(length / conf['plan_len'])

        if steps == 0:
            steps = 1
        
        log.debug("covering distance %.2f in %d steps" % (length, steps))

        # step vector: amount change per step
        step_vect = (point - prev_point) / steps
        log.debug("step vector=%s" % (step_vect))

        # for each step
        for step in range(0, steps):
            # calculate new target
            self.broken_points.append({'point': prev_point + step_vect * step })


    def check_next(self, n):
        # calc velocity acheived from previous point
        log.debug("check next n=%d" % n)
        point = self.broken_points[n]
        prev = self.broken_points[n-1]
        length = np.linalg.norm(point['point'] - prev['point'])

        a = conf['acc']
        u = prev['ltd_spd']

        v_calc_max = sqrt(pow(u,2) + 2 * a * length)
        try:
            v_calc_min = sqrt(pow(u,2) - 2 * a * length)
        except ValueError:
            v_calc_min = 0

        log.debug("v_calc_max=%.2f v_calc_min=%.2f max_spd=%.2f" % (v_calc_max, v_calc_min, point['max_spd']))
        # if we're within limits, continue
        if v_calc_max < point['max_spd']:
            log.debug('v_calc_max spd < max_spd')
            # set limited speed to max speed
            point['ltd_spd'] = v_calc_max
            # keep going forwards
            self.check_next(n+1)

        # we can't slow down in time
        elif v_calc_min > point['max_spd']:
            log.debug('max spd < v calc min')
            point['ltd_spd'] = point['max_spd']
            # then go backwards to recalculate
            self.check_prev(n-1)
            self.check_next(n+1)

        elif v_calc_max > point['max_spd']:
            log.debug('v calc max > max spd')
            # limit speed
            point['ltd_spd'] = point['max_spd']
            # keep going
            self.check_next(n+1)
        
        else:
            log.warning("shouldn't get here")

    def check_prev(self, n):
        log.debug("check prev n=%d" % n)
        point = self.broken_points[n]
        next = self.broken_points[n+1]

        length = np.linalg.norm(point['point'] - next['point'])

        a = conf['acc']
        u = next['ltd_spd']

        v_calc_max = sqrt(pow(u,2) + 2 * a * length)
        try:
            v_calc_min = sqrt(pow(u,2) - 2 * a * length)
        except ValueError:
            v_calc_min = 0
        log.debug("v_calc_max=%.2f ltd_spd=%.2f" % (v_calc_max, point['ltd_spd']))
        # do we need to limit the speed?
        if point['ltd_spd'] > v_calc_max:
            log.debug('lowered speed, go back')
            point['ltd_spd'] = v_calc_max
            self.check_prev(n-1)
        # or is the speed ok now?
        elif point['ltd_spd'] <= v_calc_max:
            log.debug('speed low enough, quit')

        log.debug("finished looking back")
        return
            

    def plan_velocity(self):
        for p in self.broken_points:
            p['ltd_spd'] = 0
        #start recursive function
        try:
            self.check_next(1)
        except IndexError:
            log.debug("plan ended")
    # for each point, calculate max rectangular velocity
    def calc_max_velocity(self):
        log.info("velocity planning %d points" % len(self.broken_points))
        for i in range(len(self.broken_points)):
            self.broken_points[i]['max_spd'] = 0
            if i > 0 and i < len(self.broken_points) - 1:
                self.broken_points[i]['max_spd'] = self.calc_speed(i)
            log.debug("max spd for point %d = %.2f" % (i, self.broken_points[i]['max_spd']))

    def calc_speed(self, i):
        rad = self.calc_rad(i)
        # tune
        spd = rad * conf['corner_spd_tune']
        # clamp
        if spd > conf['max_spd']:
            spd = conf['max_spd']
        return spd

    def calc_rad(self, i):
        A = self.broken_points[i-1]['point']
        B = self.broken_points[i]['point']
        C = self.broken_points[i+1]['point']
        a = np.linalg.norm(C - B)
        b = np.linalg.norm(C - A)
        c = np.linalg.norm(B - A)
        s = (a + b + c) / 2
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        if area == 0:
            return np.inf
        if np.isnan(area):
            return np.inf
        R = a*b*c / 4 / area
        return R
        """
        b1 = a*a * (b*b + c*c - a*a)
        b2 = b*b * (a*a + c*c - b*b)
        b3 = c*c * (a*a + b*b - c*c)
        P = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
        P /= b1 + b2 + b3
        R
        """


    def resample(self):
        self.time = []
        last_step = None
        last_step = {   'l_targ_spd' : 0,
                        'r_targ_spd' : 0,
                        'l' : 430,
                        'r' : 430,
                        }
        for step in self.steps:

            l_spd_1 = last_step['l_targ_spd']
            r_spd_1 = last_step['r_targ_spd']
            
            l_spd_2 = step['l_targ_spd']
            r_spd_2 = step['r_targ_spd']

            l_t = 2 * (step['l'] - last_step['l']) / ( l_spd_1 + l_spd_2 )
            r_t = 2 * (step['r'] - last_step['r']) / ( r_spd_1 + r_spd_2 )

            log.info("lt=%.2f rt=%.2f" % (l_t, r_t))

            log.info("%.2f -> %.2f" % (l_spd_1, l_spd_2))
            t = 0
            while t <= l_t:
                l_spd = l_spd_1 + t * ((l_spd_2 - l_spd_1) / l_t)
                r_spd = r_spd_1 + t * ((r_spd_2 - r_spd_1) / r_t)
                log.info("t=%.2f l_spd=%.2f" % (t, l_spd))
                self.time.append({
                    'l': step['l'] + l_spd * t,
                    'r': step['r'] + r_spd * t,
                    })
                t += 0.10
            last_step = step

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
            log.debug("step %d: l=%.2f @ %.2f, r=%.2f @ %.2f" % (count, step['l'], last_step['l_targ_spd'], step['r'], last_step['r_targ_spd']))

            last_step = step
            count += 1
            
        
    # open a file and dump the steps
    def output(self):
        log.info("dumping commands")
        count = 0
        # just log for now
        """
        for step in self.steps:
            log.info("step %03d: moveto x=%.2f, y=%.2f, targ spd=%.2f, l=%.2f @ %.2f, r=%.2f @ %.2f" % (count, step['x'], step['y'], step['targ_spd'], step['l'], step['l_targ_spd'], step['r'], step['r_targ_spd']))
            count += 1
        return self.steps
        """
        return self.time


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
        speed = 1 - 0.8 * (angle / 90.0)
        return speed

