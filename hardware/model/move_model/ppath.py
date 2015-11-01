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
        self.interp = []
  
    def dump(self):
        with open('points.d', 'w') as fh:
            pickle.dump({'i' : self.interp, 'p' : self.points, 'bp': self.broken_points }, fh)
        
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
        # calculate length
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
        for p in range(len(self.broken_points)):
            log.debug("p=%d ltd_spd=%.2f" % (p, self.broken_points[p]['ltd_spd']))

    # for each point, calculate max rectangular velocity
    def calc_max_velocity(self):
        log.info("velocity planning %d points" % len(self.broken_points))
        for i in range(len(self.broken_points)):
            self.broken_points[i]['max_spd'] = 0
            if i > 0 and i < len(self.broken_points) - 1:
                self.broken_points[i]['max_spd'] = self.calc_speed2(i)
#            log.debug("max spd for point %d = %.2f" % (i, self.broken_points[i]['max_spd']))

    def calc_speed(self, i):
        rad = self.calc_rad(i)
        # tune
        spd = rad * conf['corner_spd_tune']
        # clamp
        if spd > conf['max_spd']:
            spd = conf['max_spd']
        return spd

    """
    nieve calculation for now
    returns 1 for full speed, 0 for stop

    should be based on a model that takes into account :

    * weight of gondola in y 
    * minimise swing in x
    """
    def calc_speed2(self, i):
        A = self.broken_points[i-1]['point']
        B = self.broken_points[i]['point']
        C = self.broken_points[i+1]['point']
        v1 = B-A
        v2 = C-B
        angle = self.angle_between(v1,v2)
#        angle = np.degrees(angle)
        speed = 1 - math.sin(angle)
        speed *= conf['max_spd']
        log.debug("angle at %d = %.2f, max_spd=%.2f" % (i,angle,speed))
        return speed

    def unit_vector(self, vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def angle_between(self, v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::

                >>> angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                >>> angle_between((1, 0, 0), (1, 0, 0))
                0.0
                >>> angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        angle = np.arccos(np.dot(v1_u, v2_u))
        if np.isnan(angle):
            if (v1_u == v2_u).all():
                return 0.0
            else:
                return np.pi
        return angle

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


    # go through all points and work out when they are visited.
    def calc_point_times(self):
        # assign first time as 0
        self.broken_points[0]['t'] = 0
        for p in range(1,len(self.broken_points)):
            prev_point = self.broken_points[p-1]
            point = self.broken_points[p]
            length = np.linalg.norm(point['point'] - prev_point['point'])

            t = 2 *length / (point['ltd_spd']+prev_point['ltd_spd'])
            point['t'] = prev_point['t'] + t
            log.debug("visit point %d at t=%.2f" % (p, point['t']))


    # interpolate new positions from points with constant time interval
    def interpolate_pos_by_time(self):
        m = 0
        p = 0
        last_t = self.broken_points[-1]['t']
        self.interp = []
        while m <= last_t:
            # find highest point <= t
            while self.broken_points[p+1]['t'] <= m:
                p += 1
                log.debug('incrementing p = %d' % p)
            
            t = m - self.broken_points[p]['t']
            
            # interpolate between x(n),y(n) -> x(n+1),y(n+1)
            u = self.broken_points[p]['ltd_spd']
            v = self.broken_points[p+1]['ltd_spd']
            l = np.linalg.norm(self.broken_points[p]['point'] - self.broken_points[p+1]['point'])
            unit_vect =  self.broken_points[p+1]['point'] - self.broken_points[p]['point']
            a = (v-u) / (self.broken_points[p+1]['t'] - self.broken_points[p]['t'] )

            # s = ut + 0.5 (v-u)t
            #s = 0.5 * (v+u) * t
            #interp = self.broken_points[p]['point'] + (unit_vect / l) * s

            # s = ut + 0.5 * a * t^2
            s = u * t + 0.5 * a * pow(t,2)
            interp = self.broken_points[p]['point'] + (unit_vect / l) * s


            self.interp.append(interp)
            log.debug("m=%.2f t=%.2f s=%.2f u=%.2f v=%.2f xy=%s" % (m, t, s, u, v, interp))
            m += 1.00
        
