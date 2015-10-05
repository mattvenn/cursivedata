import logging

log = logging.getLogger(__name__)

class Servo():
    def __init__(self, len=100, error=1):
        self.len = len
        log.debug("initial string length {self.len}".format(**locals()))
        self.error = error
        self.run = False
    
    def set_len(self, target_len):
        self.target_len = target_len
        if self.target_len > self.len:
            self.step = self.error
        else:
            self.step = -self.error
        self.run = True

    def is_running(self):
        return self.run

    def get_len(self):
        return self.len

    def update(self):
        if abs(self.len - self.target_len) >= self.error:
            self.len += self.step
            log.debug("len={self.len}, target={self.target_len}".format(**locals()))
        else:
            self.run = False
