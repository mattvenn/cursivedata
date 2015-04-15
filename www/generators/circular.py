"""
bugs:
"""
import logging
log = logging.getLogger('generator')
from django.utils.datetime_safe import datetime
import math

def get_division(date,params):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int( date.strftime("%H") ) # minute 0 -59
    #mins in a day
    mins =  (minute + hour * 60)
    division = mins / int( params.get('circle_t') / params.get('divide') )
    division = division % params.get('divide')
    return int(division)

def get_seconds(date):
    seconds = int( date.strftime("%s") ) # minute 0 -59
    return seconds
   
def get_xy_from_div(drawing,params,div):
    #centre point
    centre = (drawing.width/2,drawing.height/2)
    circle_r = params.get("circle_r")
    angle = div * (2 * math.pi / params.get('divide'))
    x = circle_r * math.sin(angle)
    y = circle_r * math.cos(angle)
    x = centre[0] + x
    y = centre[1] - y
    return(x,y)

def process(drawing,data,params,internal_state) :
    divs = int(params.get('divide'))
    last_length = internal_state.get("last_length",[0 for i in range(divs)])
    last_div = int(internal_state.get("last_div", 0 ))
    last_val = float(internal_state.get("last_val",0))

    #we're starting - not sure about this logic
    if internal_state["start"] == 1:
        log.info("circles starting with new data")
        internal_state["start"] = 0
        last_val = float(data.get_current()[0].getValue())
        log.debug("init last_val to: %s" % last_val)

    circle_r = params.get("circle_r")
    circle_c = 2 * math.pi * circle_r
    bar_width = circle_c / params.get("divide")
    for point in data.get_current():
        #something happened to the data and we need to reset last_val
        if float(point.getValue()) < last_val:
            last_val = float(point.getValue())

        value = float(point.getValue()) - last_val
        last_val = float(point.getValue())

        div = get_division(point.date,params)
        if div != last_div:
            last_div = div 
        length = value / params.get('value')
        (x,y) = get_xy_from_div(drawing,params,div)
        angle = div * (360 / params.get('divide'))
        angle -= 180
        transform = "rotate(%d,%d,%d)" % (angle,x,y)
        log.debug("value: %s" % value)
        log.debug("div: %s" % div)
        log.debug("l length: %s" % last_length[div])
        log.debug("length: %s" % length)
        if length:
            drawing.rect(x,y+last_length[div],bar_width,length,transform = transform)
            last_length[div] += length

    internal_state["last_length"]=last_length
    internal_state["last_div"]= last_div
    internal_state["last_val"] = last_val
    return None

##all this stuff needs a bit of work, been hacked at mfuk
def begin(drawing,params,internal_state) :
    log.info("Starting circular with params: %s" % params)
    drawing.circle(drawing.width/2,drawing.height/2,params.get("circle_r",5)-5)
    divs = int(params.get('divide',1))
    internal_state["last_length"]= [0 for i in range(divs)]
    internal_state["last_div"]= 0
    internal_state["last_val"] = 0
    internal_state["start"] = 1
    text_len = 60
    text_height = 20
    drawing.text('#mfuk',drawing.width/2-text_len/2,drawing.height/2+text_height/2,size=27)
#    drawing.circle(drawing.width/2,drawing.width/2,params.get("circle_r")+20)
#    drawing.circle(drawing.width/2,drawing.width/2,params.get("circle_r")+40)
#    drawing.tl_text("Started at " + str(datetime.now()),size=15,stroke="blue")
    
def end(drawing,params,internal_state) :
    log.info("Ending drawing")
    content="Ended at " + str(datetime.now())
    drawing.bl_text(content,stroke="red",size=15)
    
def get_params() :
    return  [ 
        #changing this needs to update the internal state, as we store an array of this number
        {"name":"divide", "default": 12, "description":"divide circle into this many sections" },
        {"name":"circle_t", "default": 720, "description":"the whole circle is worth this many minutes" },
        {"name":"value", "default":50, "description":"an input value of this will draw a 1mm bar" },
        {"name":"circle_r", "default":100, "description":"radius of central circle" },
# params can only be floats        {"name":"text", "default":'text', "description":"text for centre" },
            ]

def get_name() : return "Circular"
def get_description() : return "draws a circular bar graph"

def can_run(data,params,internal_state):
    aggregate = internal_state.get("aggregate",0)
    for point in data.get_current():
        aggregate += float(point.getValue())
        if aggregate > params.get("value"):
            log.info("circles can run")
            return True
    log.info("aggregate %f < value %f so not running" % ( aggregate, params.get("value")))
    return False

