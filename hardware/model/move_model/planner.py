import math
import logging
from utils import *

log = logging.getLogger(__name__)


class Planner():
    
    # seg_len is how far we go in between calculations, so lower numbers is better
    def __init__(self, conf):
        self.conf = conf
        self.seg_len = conf['seg_len']
        self.width = conf['width']
        self.height = conf['height']

    # work through all the moves to look at speeds & angles
    def profile(self, moves):
        l_m = None
        # first pass, calculate all angles and lengths
        for m in moves:
            if l_m is None:
                l_m = m
                continue
  
            l_m['x2'] = m['x1']
            l_m['y2'] = m['y1']

            l_m = m

        # get rid of last move
        del(moves[-1])

        # then calculate speeds
        l_m = None

        for m in moves:
            m['vect'] = m['x2'] - m['x1'], m['y2'] - m['y1']
            m['len' ] = length(m['vect'])
            m['speed'] = 0 
            m['diff_angle'] = 0

            if l_m is None:
                l_m = m
                continue

            # difference between vectors
            m['diff_angle'] = angle(m['vect'],l_m['vect'])
            m['speed'] = calculate_speed(m['diff_angle'])

            l_m = m
          

    # given a move, break down into segments and calculate string lengths and servo speed ratios
    def calculate_lengths(self, move): 

        # work out steps
        steps = int(move['len'] / self.seg_len)
        # keep steps even to make acceleration easier
        if steps % 2 != 0:
            steps += 1
        if steps == 0:
            steps = 2
        log.info("planning %.2f,%.2f -> %.2f,%.2f" % (move['x1'],move['y1'],move['x2'],move['y2']))
        log.info("covering distance %.2f in %d steps" % (move['len'], steps))
        # step vector: amount change per step
        move['step_vect'] = move['vect'][0] / steps, move['vect'][1] / steps
        log.info("step vector = %.2f,%.2f" % (move['step_vect']))

        # store all the steps
        move['steps'] = []

        x = move['x1']
        y = move['y1']
        (l, r) = rect_to_polar(self.width, x, y)

        # for each step
        for step in range(1,steps+1):
            # calculate new target
            xstep = x + move['step_vect'][0] * step
            ystep = y + move['step_vect'][1] * step
            # calculate new string lengths
            (newl, newr) = rect_to_polar(self.width, xstep, ystep)
            ratio = (newl-l)/(newr-r)
            move['steps'].append({ 'l': newl, 'r': newr, 'ratio': ratio})
            log.info("ldiff=%.2f rdiff=%.2f ratio=%.2f" % (newl-l, newr-r, ratio) )

            # set the new x and y
            l = newl
            r = newr

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

        # can't accelerate so much we go over the top speed of servo
        max_mult = self.conf['max_spd'] / max_spd
        log.info("max speed = %.2f so max mult = %.2f" % (max_spd, max_mult))

        slow_down_step = steps
        for move in moves:
            # accelerate phase
            if step < steps/2:
                new_acc = acc + self.conf['acc']
                # limit speed
                if new_acc >= max_mult:
                    new_acc = max_mult
                acc_hist.append(new_acc)
                acc = new_acc
            # decellerate with same profile
            else:
                acc = acc_hist.pop()

            move['ls'] *= acc
            move['rs'] *= acc
            log.info("step = %d, acc = %.2f, ls = %.2f, rs = %.2f" % (step, acc, move['ls'], move['rs']))
            step += 1

        return moves
