from django.utils.datetime_safe import datetime
import logging
import math
log = logging.getLogger('generator')
from pysvg.builders import *

def get_division(date,params):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int( date.strftime("%H") ) # minute 0 -59
    dom = int( date.strftime("%d") ) #day of month 0 - 31

    #mins in the month
    mins =  minute + hour * 60 + dom * 24 * 60
    div = mins % int(params.get('spiral_t'))
        
    return div

def get_xy_from_div(drawing,params,div):
    #centre point
    centre = (drawing.width/2,drawing.height/2)
    inner_r = params.get("spiral_inner_r")
    outer_r = params.get("spiral_outer_r")
    angle = div * (params.get('loops') * 2 * math.pi / params.get('spiral_t'))
    distance = inner_r + (div / params.get('spiral_t')) * (outer_r - inner_r)
#    log.debug("dist = %2.2f, angle = %2.2f" % (distance,angle))
    x = distance * math.sin(angle)
    y = distance * math.cos(angle)
    x = centre[0] + x
    y = centre[1] - y
    return(x,y,angle)

def draw_leaf(drawing,x,y,rotate,width,num=1):
    
    leaf = drawing.get_first_group_from_file("media/atbristol-petals/petal-%d.svg" % num)
    th=TransformBuilder()
    th.setScaling( width ) 
    th.setRotation( rotate )
    th.setTranslation( "%d,%d" % ( x ,y ) )
    leaf.set_transform(th.getTransform())
    drawing.doc.addElement(leaf)

def get_minute(date):
    minute = int( date.strftime("%M") ) # minute 0 -59
    return minute

def process(drawing,data,params,internal_state) :
    log.debug("processing data with parameters %s" % params)
#    aggregate = internal_state.get("aggregate",0)
    aggregate = 0
    points = 0
    
    #Run through all the data points
    for point in data.get_current():
        points += 1
        aggregate += float(point.getValue())

        if True:
            if aggregate > params.get("value"):
            #    log.debug("drawing...")
                minute = get_minute(point.date)
                size = aggregate/params.get("petal_scaling")
                petal_type = 1
                if size > 0.3:
                    petal_type = 3
                elif size > 0.15:
                    petal_type = 2
                div = get_division(point.date,params)
                (x1,y1,angle) = get_xy_from_div(drawing,params,div)
                angle -= math.pi / 16
                log.debug("points %d size %f, xy=%d,%d a=%f, type=%d" % (points, size,x1,y1,angle,petal_type))

                draw_leaf(drawing,x1,y1,math.degrees(angle),size,petal_type)
                aggregate = 0
                points = 0
            #else:
            #    aggregate = 0
        
#    internal_state["aggregate"]=aggregate
    return None

def begin(drawing,params,internal_state) :
    log.info("starting with params %s" % params)
    
def end(drawing,params,internal_state) :
    log.info("ending")
    
def get_params() :
    return  [ 
        {"name":"spiral_t", "default": 1440, "description":"the whole spiral is worth this many minutes (max is one months worth)" },
        {"name":"value", "default":80000, "description":"an input value of this will draw a petal" },
        {"name":"petal_scaling", "default":1, "description":"how much petals are scaled by" },
        {"name":"loops", "default":4, "description":"how many loops the spiral makes" },
        {"name":"spiral_outer_r", "default":150, "description":"radius of outside of spiral" },
        {"name":"spiral_inner_r", "default":50, "description":"radius of inside of spiral" },
             ] 

def get_name() : return "atbristol petals"
def get_description() : return "draws petals around a spiral"

def can_run(data,params,internal_state):
    
    aggregate = internal_state.get("aggregate",0)
    for point in data.get_current():
        aggregate += float(point.getValue())
        # if enough energy
        if aggregate > params.get("value"):
            log.info("can run")
            # and 5 minute mark
            if get_minute(point.date) % 2 == 0:
                return True
    return False
