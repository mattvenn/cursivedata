import logging
import random
from conf import conf
log = logging.getLogger(__name__)

class Servo():
    def __init__(self, len=100, name=''):
        self.len = len
        self.targ_len = len
        self.spd_err = conf['spd_err']
        self.name = name
        self.updates = 0
        log.info("{self.name}: initial string length {self.len:.2f}".format(**locals()))
        self.spd = 0
        self.targ_spd = 0
        self.finish = True
    
    def set_len(self, targ_len, targ_spd):
        self.finish = False

        self.start_len = self.len
        self.start_spd = self.spd

        self.targ_spd = targ_spd
        self.targ_len = targ_len
        log.info("%.2f @ %.2f going to %.2f @ %.2f" % (self.len, self.spd, targ_len, targ_spd))

    def finished(self):
        return self.finish

    def get_len(self):
        return self.len

    def update(self):
        self.updates += 1

        self.len += self.spd

        # end conditions
        if self.len_error() < conf['len_err']:
            self.finish = True
        
        log.debug("{self.name}: len={self.len:.2f}, target={self.targ_len:.2f} spd={self.spd:.3f} targ_spd={self.targ_spd:.3f}".format(**locals()))
       
    def len_error(self):
        return abs(self.len - self.targ_len)

    def spd_error(self):
        return abs(self.spd - self.targ_spd)

    def calculate_acc_dist(self):
        
        s_1 = float(self.spd)
        l = self.len_error()
        s_2 = float(self.targ_spd)

        # distance convered while changing speed
        # v1^2 - v0^2 = 2 * a * s
        acc_l = (s_2 * s_2 - s_1 * s_1 ) / ( 2 * conf['servo_acc'])
        if acc_l > l: 
            raise Exception("l is too short given speeds and acc")
        log.info("cover distance %.2f during acc" % acc_l)
        return acc_l

        
        return td

        
