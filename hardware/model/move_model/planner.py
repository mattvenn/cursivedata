import math
import logging

log = logging.getLogger(__name__)


class Planner():
    
    # seg_len is how far we go in between calculations, so lower numbers is better
    def __init__(self, width, height, seg_len=3.0):
        self.seg_len = seg_len
        self.width = width
        self.height = height

    def polar_to_rect(self, a, c):
        b = self.width
        i = (a*a+b*b-c*c)/(2.0*a*b)
        x = i * a
        try:
            y = math.sqrt(1.0 - i*i)*a
        except ValueError:
            print("value error")
            y = 0
        return(x,y)

    def rect_to_polar(self,x,y):
        l = math.sqrt(pow(x,2)+pow(y,2))
        r = math.sqrt(pow((self.width-x),2)+pow(y,2))
        return(l,r)

    def calculate_distance(self, x1,y1,x2,y2):
         dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
         return dist

    # given starting xy and ending xy, plan a set of moves
    def plan(self, x, y, newx, newy): 
#        import ipdb; ipdb.set_trace()
        moves = []
        len = self.calculate_distance(x,y,newx,newy)

        # work out steps
        steps = int(len / self.seg_len)
        log.info("covering distance %d in %d steps" % (len, steps))
        unitvect = (float(newx-x)/steps , float(newy - y)/steps)
        log.info("unitvector = %f,%f" % (unitvect))

        for step in range(1,steps+1):
            xstep = x + unitvect[0] * step
            ystep = y + unitvect[1] * step
            log.info("x = %.2f, y = %.2f" % (xstep, ystep))
            (l, r) = self.rect_to_polar(xstep, ystep)
            moves.append({ 'l': l, 'ls': 1, 'r': r, 'rs': 1})
        return moves

