import logging
import pickle
import math
from conf import conf
from bokeh.plotting import figure, output_file, show, ColumnDataSource, gridplot
from bokeh.properties import Color

logging.basicConfig(level=logging.INFO)

file_name = 'square.d'

def polar_to_rect(a, c, b):
    gamma = math.acos((a*a+b*b-c*c)/(2.0*a*b))
    y = math.sin(gamma) * a
    x = math.cos(gamma) * a
    return(x,y)

with open(file_name) as fh:
    points = pickle.load(fh)

logging.info("file is %d points long" % len(points['i']))

# width error calculations:
# change width supplied to the x,y calc
def width_error_calc(width,orig_width):
    x = []
    y = []
    for p in points['i']:
        a = p['a']
        b = p['b']
        try:
            nx, ny = polar_to_rect(a, b, width)
            # compensate for shifting x
            nx += (orig_width - width ) / 2
            x.append(nx)
            y.append(ny)
        except ValueError as e:
            logging.debug("skipping %f,%f" % (a,b))

    source = ColumnDataSource(
            data=dict(
                x=x,
                y=y,
            ))
    return source

# spool diameter error calculations:
# these errors build up depending on how long the string is
def spool_error_calc(diameter_err):
    x = []
    y = []
    for p in points['i']:
        a = p['a']
        b = p['b']
        a += a * diameter_err
        b += b * diameter_err

        try:
            nx, ny = polar_to_rect(a, b, width)
            x.append(nx)
            y.append(ny)
        except ValueError as e:
            logging.debug("skipping %f,%f" % (a,b))

    source = ColumnDataSource(
            data=dict(
                x=x,
                y=y,
            ))
    return source

TOOLS = 'wheel_zoom,hover,pan,tap,resize,reset'
# output to static HTML file
output_file("lines.html", title="line plot example")

width = conf['width']
height = conf['height']

p_w_err = figure(title="width errors", tools=TOOLS, x_range=(0,width), y_range=(height,0))

i = 0
# do 20 variations
for err in range(int(width * 0.8), int(width * 1.2), int(width/50)):
    logging.info("width = %d" % err)
    i+=1
    shade = (255 / 20) * i
    source = width_error_calc(err, width)
    p_w_err.line('x', 'y', source=source, line_color=(128,128,shade))


p_s_err = figure(title="spool errors", tools=TOOLS, x_range=(0,width), y_range=(height,0))

i = 0
# do 20 variations
for err in range(-10,10):
    logging.info("spool err = %f" % (err / 100.0))
    source = spool_error_calc(err / 100.0)
    i+=1
    shade = (255 / 20) * i
    p_s_err.line('x', 'y', source=source, line_color=(128,128,shade))

#show(p_s_err)

p = gridplot([[p_w_err,p_s_err]])
show(p)
