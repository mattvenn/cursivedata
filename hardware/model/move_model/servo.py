import logging
import random
from conf import conf
log = logging.getLogger(__name__)


class Servo():
    def __init__(self, len=100, name=''):
        self.len = len
        self.target_len = len
        self.spd_err = conf['spd_err']
        self.name = name
        self.updates = 0
        log.info("{self.name}: initial string length {self.len:.2f}".format(**locals()))
        self.spd = 0
        self.targ_spd = 0
        self.finish = True
    
    def set_len(self, targ_len, targ_spd=0):
        self.updates = 0
        self.finish = False
        self.targ_spd = targ_spd
        # limit speeds - needs to work for -ve too
        """
        if targ_spd > conf['max_spd']:
            log.error("%s: limiting speed from %.2f to %.2f!" % (self.name, self.targ_spd, conf['max_spd']))
            self.targ_spd = conf['max_spd']
        """

        self.targ_len = targ_len

    def finished(self):
        return self.finish

    def get_len(self):
        return self.len

    def log_error(self):
        log.info("%s: len err=%.2f, spd err=%.2f" % (self.name, self.len - self.targ_len, self.spd - self.targ_spd))

