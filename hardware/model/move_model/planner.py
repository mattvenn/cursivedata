import math
import logging
from utils import rect_to_polar, polar_to_rect, calculate_distance

log = logging.getLogger(__name__)


class Planner():
    
    # seg_len is how far we go in between calculations, so lower numbers is better
    def __init__(self, conf):
        self.servo_max = conf['max_spd']
        self.seg_len = conf['seg_len']
        self.width = conf['width']
        self.height = conf['height']

    # given starting xy and ending xy, plan a set of moves
    def plan(self, x, y, newx, newy, l, r): 
        log.info("l = %.2f r = %.2f" % (l,r))
        log.info("newl = %.2f newr = %.2f" % rect_to_polar(self.width, newx, newy))
        moves = []
        len = calculate_distance(x,y,newx,newy)

        # work out steps
        steps = int(len / self.seg_len)
        log.info("covering distance %.2f in %d steps" % (len, steps))

        # unit vector: amount change per step
        unitvect = (float(newx-x)/steps , float(newy - y)/steps)
        log.info("unitvector = %f,%f" % (unitvect))

        # for each step
        for step in range(1,steps+1):
            # calculate new target
            xstep = x + unitvect[0] * step
            ystep = y + unitvect[1] * step
            log.debug("x = %.2f, y = %.2f" % (xstep, ystep))
            # calculate new string lengths
            (newl, newr) = rect_to_polar(self.width, xstep, ystep)
            # work out the speeds
            if abs(newl-l) > abs(newr-r):
                ls = 1
                rs = abs(newr-r)/abs(newl-l)
            elif abs(newl-l) < abs(newr-r):
                rs = 1
                ls = abs(newl-l)/abs(newr-r)
            else:
                rs = 1
                ls = 1
            log.error("l %.2f r %.2f newl %.2f newr %.2f ls %.2f rs %.2f" % (l, r, newl, newr, ls, rs))
            # normalise to max servo speed
            ls *= self.servo_max
            rs *= self.servo_max

            moves.append({ 'l': newl, 'ls': ls, 'r': newr, 'rs': rs})
            log.debug("l = %.2f, r = %.2f, ls = %.2f, rs = %.2f" %
                (l, r, ls, rs))

            # set the new left and right string lengths
            l = newl
            r = newr
        return moves

