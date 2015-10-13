import math
import logging
from utils import *

log = logging.getLogger(__name__)

# contains all the paths
class Moves():
    def __init__(self, conf, x, y):
        self.paths = []
        self.conf = conf
        p = Path(conf)
        self.paths.append(p)
        self.x = x
        self.y = y
   
    def add_point(self, x, y):
        s = Segment(self.conf, self.x, self.y, x, y)
        self.x = x
        self.y = y
        # not a great way of doing this
        if not self.paths[-1].add_segment(s):
            log.info("ending path")
            log.info("appended segment %s" % s)
            self.paths.append(Path(self.conf))
            self.paths[-1].add_segment(s)
        else:
            log.info("appended segment %s" % s)
       
    def process(self):
        for p in self.paths:
            log.info("processing path")
            for s in p.segments:
                log.info(s)

# paths start and stop at 0 speed
class Path():
    def __init__(self, conf):
        self.segments = []
        self.conf = conf
        self.angle = 0

    def add_segment(self, segment):
        if len(self.segments):
            self.angle = self.segments[-1].angle(segment)
            if self.angle >= 90:
                return False
        self.segments.append(segment)
        return True

    # nieve calculation for now
    # returns 1 for full speed, 0 for stop
    def calculate_speed(self, angle):
        if angle > 90:
            angle = 90
        speed = 1 - (angle / 90.0)
        speed *= 0.8
        return speed

# segments are each straight line in a path
class Segment():
    def __init__(self, conf, x1, y1, x2, y2):
        self.conf = conf
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        (self.l1, self.r1) = rect_to_polar(self.conf['width'], x1, y1)
        (self.l2, self.r2) = rect_to_polar(self.conf['width'], x2, y2)
        self.v = [x1 - x2, y1 - y2]
        self.ratio = (self.l1 - self.l2) / (self.r1 - self.r2)

    def dotproduct(self, vect):
      return sum((a*b) for a, b in zip(self.v, vect.v))

    def length(self):
      return math.sqrt(self.dotproduct(self))

    def angle(self, vect):
      return math.degrees(math.acos(self.dotproduct(vect) / (self.length() * vect.length())))

    def __str__(self):
        return "%.2f,%.2f -> %.2f,%.2f ratio=%.2f" % (self.x1,self.y1,self.x2,self.y2, self.ratio)


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
        count = 0
        for m in moves:
            m['count'] = count
            count += 1

            if l_m is None:
                l_m = m
                continue
  
            l_m['x2'] = m['x1']
            l_m['y2'] = m['y1']

            l_m = m

        # get rid of last move as each move now has a start and endpoint
        del(moves[-1])

        # calculate speeds by looking at the angular difference between moves
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
        step_list = []

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
            step_list.append({ 'l': newl, 'r': newr, 'ratio': ratio})
            log.info("ldiff=%.2f rdiff=%.2f ratio=%.2f" % (newl-l, newr-r, ratio) )

            # set the new x and y
            l = newl
            r = newr
        return step_list

    # process all the moves and break them into separate chunks that begin and end at 0 speed
    def break_paths(self, moves):
        sub_moves = []
        sub_move = []
        for m in moves:
            sub_move.append(m)
            if m['speed'] == 0:
                sub_moves.append(sub_move)
                sub_move = []
            log.info(len(sub_move))
            
        sub_moves.append(sub_move)
        log.info("broke %d moves into %d sub moves" % (len(moves),len(sub_moves)))
        return sub_moves


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
