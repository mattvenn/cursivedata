import logging
import random

log = logging.getLogger(__name__)


class Servo():
    def __init__(self, conf, len=100, name=''):
        self.len = len
        self.spd_err = conf['spd_err']
        self.name = name
        self.updates = 0
        log.info("{self.name}: initial string length {self.len:.2f}".format(**locals()))
        self.max_spd_lmt = conf['max_spd']
        self.max_spd = 0
        self.run = False
    
    def set_len(self, target_len, speed=1):
        # store top speed for stats
        if speed > self.max_spd:
            self.max_spd = speed
        # ensure our ending condition is met
        if speed > self.max_spd_lmt:
            log.error("%s: limiting speed from %.2f to %.2f!" % (self.name, speed, self.max_spd_lmt))
            speed = self.max_spd_lmt
        log.debug("%s: cur = %.2f target = %.2f speed = %.4f" % (self.name, self.len, target_len, speed))
        self.target_len = target_len
        if self.target_len > self.len:
            self.step = speed
        else:
            self.step = -speed
        self.run = True

    def is_running(self):
        return self.run

    def get_len(self):
        return self.len

    def update(self):
        if self.run == False:
            return
        self.updates += 1

        # add a random speed error
        speed_error = 2 * (1.0 - random.random()) * self.spd_err * self.step

        log.debug("{self.name}: len={self.len:.2f}, target={self.target_len:.2f} spd={self.step:.3f}".format(**locals()))
        self.len += self.step + speed_error

        # getting longer
        if self.step > 0 and self.len >= self.target_len:
            #these mean lengths are always accurate
            #figure out a more accurate way of modelling this?
            self.len = self.target_len
            self.run = False
        # getting shorter
        if self.step < 0 and self.len <= self.target_len:
            self.len = self.target_len
            self.run = False
            
