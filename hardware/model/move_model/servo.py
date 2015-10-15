import logging
import random
from conf import conf
log = logging.getLogger(__name__)


class Servo():
    def __init__(self, conf, len=100, name=''):
        self.len = len
        self.spd_err = conf['spd_err']
        self.name = name
        self.updates = 0
        log.info("{self.name}: initial string length {self.len:.2f}".format(**locals()))
        self.speed = 0
        self.targ_spd = 0
        self.finish = True
    
    def set_len(self, target_len, targ_spd=0):
        self.finish = False
        self.targ_spd = targ_spd
        # limit speeds
        if targ_spd > conf['max_spd']:
            log.error("%s: limiting speed from %.2f to %.2f!" % (self.name, speed, self.max_spd_lmt))
            self.targ_spd = conf['max_spd']


        self.target_len = target_len

    def finished(self):
        return self.finish

    def get_len(self):
        return self.len

    def update(self):
        self.updates += 1

        # add a random speed error
        #speed_error = 2 * (1.0 - random.random()) * self.spd_err * self.step

        log.debug("{self.name}: len={self.len:.2f}, target={self.target_len:.2f} spd={self.speed:.3f} targ_spd={self.targ_spd:.3f}".format(**locals()))
        #self.len += self.step + speed_error

        self.len += self.speed
        #PI control
        P = 0.1
        error = self.speed - self.targ_spd
        self.speed += error * P

        if abs(self.len - self.target_len) < 1:
            self.finish = True
            
