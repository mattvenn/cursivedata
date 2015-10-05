import logging

log = logging.getLogger(__name__)

class Servo():
    def __init__(self, len=100, error=0.5):
        self.len = len
        log.debug("initial string length {self.len}".format(**locals()))
        self.error = error
        self.run = False
    
    def set_len(self, target_len, speed=1):
        # ensure our ending condition is met
        if speed > self.error:
            speed = self.error

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
        if abs(self.len - self.target_len) >= self.error:
            self.len += self.step
            log.debug("len={self.len}, target={self.target_len}".format(**locals()))
        else:
            self.run = False
