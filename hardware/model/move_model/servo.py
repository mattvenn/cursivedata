import logging

log = logging.getLogger(__name__)

class Servo():
    def __init__(self, len=100, max_speed=0.5, error=2, name=''):
        self.len = len
        self.error = error
        self.name = name
        log.info("{self.name}: initial string length {self.len:.2f}".format(**locals()))
        self.max_speed = max_speed
        self.run = False
    
    def set_len(self, target_len, speed=1):
        # ensure our ending condition is met
        if speed > self.max_speed:
            speed = self.max_speed
        log.info("%s: cur = %.2f target = %.2f speed = %.4f" % (self.name, self.len, target_len, speed))
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
        if abs(self.len - self.target_len) >= (self.error):
            self.len += self.step
            log.debug("{self.name}: len={self.len:.2f}, target={self.target_len:.2f} spd={self.step:.3f}".format(**locals()))
        else:
            self.run = False
