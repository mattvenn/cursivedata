import math
import logging
from utils import rect_to_polar, polar_to_rect, calculate_distance

log = logging.getLogger(__name__)


class Planner():
    
    # seg_len is how far we go in between calculations, so lower numbers is better
    def __init__(self, conf):
        self.conf = conf
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
        # keep steps even to make accelleration easier
        if steps % 2 != 0:
            steps += 1
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
                ls = self.conf['min_spd'] * abs(newl-l)/abs(newr-r)
                rs = self.conf['min_spd']
            elif abs(newl-l) < abs(newr-r):
                rs = self.conf['min_spd'] * abs(newr-r)/abs(newl-l)
                ls = self.conf['min_spd']
            else:
                rs = self.conf['min_spd']
                ls = self.conf['min_spd']

            log.info("l %03.2f r %03.2f newl %03.2f newr %03.2f ls %.2f rs %.2f" % (l, r, newl, newr, ls, rs))

            moves.append({ 'l': newl, 'ls': ls, 'r': newr, 'rs': rs})

            # set the new left and right string lengths
            l = newl
            r = newr
        return moves

    def accel(self, moves):
        steps = len(moves)
        step = 0
        acc = 1
        acc_hist = []
        max_spd = 0
        for move in moves:
            if move['ls'] > max_spd:
                max_spd = move['ls']
            if move['rs'] > max_spd:
                max_spd = move['rs']

        # can't accellerate so much we go over the top speed of servo
        max_mult = self.conf['max_spd'] / max_spd
        log.info("max speed = %.2f so max mult = %.2f" % (max_spd, max_mult))

        slow_down_step = steps
        for move in moves:
            # accellerate phase
            if step < steps/2:
                new_acc = acc + self.conf['acc']
                # only use new acc if result is less than max servo speed
                if new_acc <= max_mult:
                    acc = new_acc
                acc_hist.append(acc)
            # decellerate with same profile
            else:
                acc = acc_hist.pop()

            move['ls'] *= acc
            move['rs'] *= acc
            log.info("step = %d, acc = %.2f, ls = %.2f, rs = %.2f" % (step, acc, move['ls'], move['rs']))
            step += 1

        return moves
