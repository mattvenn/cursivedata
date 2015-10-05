import logging
from PIL import Image, ImageDraw
log = logging.getLogger(__name__)

RED = (255,0,0)
BLUE = (0,0,255)

class Canvas():

    def __init__(self, width, height, scaling=8):
        self.scaling = scaling
        self.w = width * scaling
        self.h = height * scaling
        #create an image
        self.im = Image.new("RGB", (self.w, self.h), "white")
        #get the draw object
        self.draw = ImageDraw.Draw(self.im)
        self.last_xy = None

    def update(self, pen, xy):
        # validation here later
        if self.last_xy is None:
            self.last_xy = xy
            return
        x1 = self.last_xy[0] * self.scaling
        y1 = self.last_xy[1] * self.scaling
        x2 = xy[0] * self.scaling
        y2 = xy[1] * self.scaling
        log.debug("plotting {pen} at {x2:.2f},{y2:.2f}".format(**locals()))
        log.debug("{x1},{y1} -> {x2},{y2}".format(**locals()))
        if pen:
            colour = RED
        else:
            colour = BLUE
        self.draw.line((x1,y1,x2,y2), fill=colour, width=3)
        self.last_xy = xy
    
    def save(self):
        self.im.save("test.png", "PNG")
