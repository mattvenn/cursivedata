import logging
from PIL import Image, ImageDraw, ImageFont
log = logging.getLogger(__name__)

RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)

class Canvas():

    def __init__(self, conf):
        self.scaling = conf['scaling']
        self.w = conf['width'] * self.scaling
        self.h = conf['height'] * self.scaling
        self.last_xy = None

        # create an image
        self.im = Image.new("RGB", (self.w, self.h), "white")

        # get the draw object
        self.draw = ImageDraw.Draw(self.im)

        # write some info
        font_path = '/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf'

        font_size = 80
        font = ImageFont.truetype(font_path, font_size)
        y = 0
        size_str = "%dx%dcm" % (conf['width'], conf['height'])
        self.draw.text([0,y], size_str, font=font, fill="black")
        y += font_size
        err_str = "servo: max spd = %s, spd err = %s%%, len err = %dcm" % (conf['max_spd'], conf['spd_err']*100, conf['len_err'])
        self.draw.text([0,y], err_str, font=font, fill="black")
        y += font_size
        err_str = "planner: seg len = %dcm" % (conf['seg_len'])
        self.draw.text([0,y], err_str, font=font, fill="black")


    def draw_line(self, pen, xy):
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
        self.draw.line((x1,y1,x2,y2), fill=colour, width=self.scaling)
        self.last_xy = xy
   
    def show_move(self, xy):
        rad = self.scaling
        x = xy[0] * self.scaling
        y = xy[1] * self.scaling
        self.draw.ellipse((x-rad, y-rad, x+rad, y+rad), fill=GREEN)

    def save(self):
        self.im.save("test.png", "PNG")
