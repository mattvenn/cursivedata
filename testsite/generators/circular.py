"""
bugs:
  with squareIncMM an odd number, the squares don't join up properly...
"""
from django.utils.datetime_safe import datetime
import math

def get_division(date,params):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int( date.strftime("%H") ) # minute 0 -59
    #mins in a day
    mins =  (minute + hour * 60)
    division = mins / int( params.get('circle_t') / params.get('divide') )
    division = division % params.get('divide')
    return division

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
    last_length = internal_state.get("last_length",0)
    last_div = internal_state.get("last_div", 0 )

    circle_r = params.get("circle_r")
    circle_c = 2 * math.pi * circle_r
    bar_width = circle_c / params.get("divide")
    for point in data.get_current():
        div = get_division(point.date,params)
        print div
        if div != last_div:
            last_length = 0
            last_div = div 
        length = float(point.data['value']) / params.get('value')
        (x,y) = get_xy_from_div(drawing,params,div)
        angle = div * (360 / params.get('divide'))
        angle -= 180
        transform = "rotate(%d,%d,%d)" % (angle,x,y)
        drawing.rect(x,y+last_length,bar_width,length,transform = transform)
#        drawing.text(div,x,y,size=20,transform = transform)
        last_length += length

    internal_state["last_length"]=last_length
    internal_state["last_div"]=last_div
    return None

def begin(drawing,params,internal_state) :
    print "Starting drawing squares: ",map(str,params)
    drawing.circle(drawing.width/2,drawing.width/2,params.get("circle_r"))
    drawing.tl_text("Started at " + str(datetime.now()),size=15,stroke="blue")
    
def end(drawing,params,internal_state) :
    print "Ending drawing with params:",map(str,params)
    content="Ended at " + str(datetime.now())
    drawing.bl_text(content,stroke="red",size=15)
    
def get_params() :
    return  [ 
        {"name":"divide", "default": 12, "description":"divide circle into this many sections" },
        {"name":"circle_t", "default": 720, "description":"the whole circle is worth this many minutes" },
        {"name":"value", "default":50, "description":"an input value of this will draw a 1mm bar" },
        {"name":"circle_r", "default":100, "description":"radius of central circle" },
            ]

def get_name() : return "Circular"
def get_description() : return "draws a circular bar graph"

def can_run(data,params,internal_state):
    aggregate = internal_state.get("aggregate",0)
    for point in data.get_current():
        aggregate += float(point.data['value'])
        if aggregate > params.get("value"):
            print "circles can run"
            return True
    print "aggregate %f < value %f so not running" % ( aggregate, params.get("value") )
    return False

