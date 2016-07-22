"""
bugs:
"""
from django.utils.datetime_safe import datetime
import math
import logging
log = logging.getLogger('generator')

def get_division(date,params,internal_state):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int( date.strftime("%H") ) # minute 0 -59
    dom = int( date.strftime("%d") ) #day of month 0 - 31

    #mins in the month
    mins =  minute + hour * 60 + dom * 24 * 60
    div = mins % params.get('circle_t')
        
    return div

def get_xy(drawing,params,radius,div):
    #centre point
    centre = (drawing.width/2,drawing.height/2)
    angle = div * (2 * math.pi / params.get('circle_t'))
    x = radius * math.sin(angle)
    y = radius * math.cos(angle)
    x = centre[0] + x
    y = centre[1] - y
    return(x,y)

def process(drawing,data,params,internal_state) :

    circle_r = params.get("circle_r")

    for point in data.get_current():

        div = get_division(point.date,params,internal_state)
        value = float(point.getValue())
        length = (value / params.get('value'))*circle_r
        if length > circle_r:
            length = circle_r
        #guess at minimum drawable line length
        if length < 1:
            length = 0
        (x2,y2) = get_xy(drawing,params,circle_r,div)
        (x1,y1) = get_xy(drawing,params,circle_r-length,div)

        if length:
            drawing.line(x1,y1,x2,y2)

    return None

##all this stuff needs a bit of work, been hacked at mfuk
def begin(drawing,params,internal_state) :
    pass
    
def end(drawing,params,internal_state) :
    pass
    
def get_params() :
    return  [ 
        #changing this needs to update the internal state, as we store an array of this number
        {"name":"circle_t", "default": 1440, "description":"the whole circle is worth this many minutes (max is one months worth)" },
        {"name":"value", "default":1000, "description":"maximum value expected - draws line of length r" },
        {"name":"circle_r", "default":100, "description":"radius of central circle" },
# params can only be floats        {"name":"text", "default":'text', "description":"text for centre" },
            ]

def get_name() : return "Circular"
def get_description() : return "draws a circular bar graph"

def can_run(data,params,internal_state):
    return True

