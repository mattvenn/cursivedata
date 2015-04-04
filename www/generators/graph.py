"""
todo:
    add labelled axis
    ability to set a ymin
"""
from django.utils.datetime_safe import datetime
import logging
log = logging.getLogger('generator')

def get_x(point,params):
    return get_minute(point.date) % params.get("MaxTime")

#turns a date into minutes
def get_minute(date):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    mins =  (minute + hour * 60) # 0 - 1439
    return mins

def process(drawing,data,params,internal_state) :
    
    #Read in parameters

    oldx = internal_state.get("oldx",0) 
    oldy = internal_state.get("oldy",0) 
    x_scale = drawing.width / float(params.get("MaxTime"))
    y_scale = drawing.height / float(params.get("MaxY"))
    height = drawing.height
    
    #Run through all the data points
    for point in data.get_current():
        y = float(point.getValue())
        if y > params.get("MaxY"):
            y = params.get("MaxY")
        #flip y
        y = params.get("MaxY") - y
        #do this as a function so can also call from can_run
        x = get_x(point,params)
        #import pdb; pdb.set_trace()
        #if we wrap back round, don't draw the connecting line, just update old x and y
        if x < oldx or (x - oldx) > params.get("SkipDrawTime"):
            log.debug("not drawing, wrapping")
            log.debug("x: %d oldx: %d, skip time: %d" % (x, oldx, params.get("SkipDrawTime")))
            oldx = x
            oldy = y
            continue
        log.debug("drawing %d,%d -> %d,%d" % (oldx,oldy,x,y))
        drawing.line(oldx*x_scale,oldy*y_scale,x*x_scale,y*y_scale)
        oldx = x
        oldy = y
        
    #Write back any state we want to keep track of
    internal_state["oldx"]=oldx
    internal_state["oldy"]=oldy
    return None

def begin(drawing,params,internal_state) :
    log.info("Starting graph with params %s" % map(str,params))
    
def end(drawing,params,internal_state) :
    log.info("Ending graph")
    
def get_params() :
    return  [ 
             { "name":"MaxTime", "default": 10, "description":"Max time for X axis (minutes)" }, 
             { "name":"MaxY", "default":10, "description":"Max Y axis" },
             { "name":"SkipDrawTime", "default":20, "description":"how many minutes pass before we lift the pen to move" },
             ]

def get_name() : return "Graph Generator"
def get_description() : return "draws a simple line graph"

#only draw if time has moved on
def can_run(data,params,internal_state):
#    import pdb;pdb.set_trace()
    for point in data.get_current():
        x = get_x(point,params)
        if x != internal_state.get("oldx"):
            return True;
    return False
