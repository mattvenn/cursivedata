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
        self.start_spd = self.spd
        self.targ_spd = targ_spd
        # limit speeds
        #if targ_spd > conf['max_spd']:
        #    log.error("%s: limiting speed from %.2f to %.2f!" % (self.name, speed, self.max_spd_lmt))
        #    self.targ_spd = conf['max_spd']


        self.targ_len = targ_len

        # how long it should roughly take
        t = self.len_error() / self.spd_error()
        self.spd_change_time = self.calculate_acc_time(t)
        log.debug(self.spd_change_time)

    def finished(self):
        return self.finish

    def get_len(self):
        return self.len

    def update(self):
        self.updates += 1

        log.debug("{self.name}: len={self.len:.2f}, target={self.targ_len:.2f} spd={self.spd:.3f} targ_spd={self.targ_spd:.3f}".format(**locals()))
        #self.len += self.step + speed_error

        if self.updates > self.spd_change_time:
            self.spd += self.targ_spd - self.conf['servo_acc']

        if self.targ_len < self.len:
            self.spd += conf['servo_acc']

        if self.spd > conf['max_spd']:
            self.spd = conf['max_spd']
        if self.spd < - conf['max_spd']:
            self.spd = - conf['max_spd']

        self.len += self.spd

        if self.len_error() < conf['len_err']:
            self.finish = True
       
    def len_error(self):
        return abs(self.len - self.targ_len)

    def spd_error(self):
        return abs(self.spd - self.targ_spd)

    def calculate_acc_time(self, t):
        
        s_s = float(self.spd)
        l = self.len_error()
        s_t = float(self.targ_spd)

        # check values first
        if (abs(s_s - s_t) / t) > conf['servo_acc']:
            raise Exception("impossible to acc/dec in time")

        td = ( 2 * l - t * abs(s_t - s_s)) / abs(s_t - s_s) 
        if s_t > s_s:
            td = t - td 
        if td < 0:
            raise Exception("impossible to acheive length in time")
        return td

        
