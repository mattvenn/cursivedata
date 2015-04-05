"""
bugs:
"""
from django.utils.datetime_safe import datetime
from pysvg.builders import *
import pysvg.structure
import math
import random

import logging
log = logging.getLogger('generator')

def get_minute(date):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    mins =  (minute + hour * 60)
    return mins

def process(drawing,data,params,internal_state) :
    aggregate = 0
    minute = int(internal_state.get("minute",0))
    interval = int(params.get("interval",10))

    for point in data.get_current():
        current_minute = get_minute(point.date) 
        aggregate += float(point.data['value'])
        log.debug("aggregate: %s" % aggregate)
        log.debug("current minute: %s" % current_minute)
        log.debug("minute + interval: %s" % (minute + interval))
        #if we've got enough time & aggregate to draw a leaf
        if (current_minute > (minute + interval)) and aggregate > 0:

            rotate = random.randint(0,360)
            scale = float(params.get("value",1))
            #work out where to draw
            border = drawing.width / 10
            startx = 0
            starty = 0
            startx =  random.randint(border, drawing.width-border)
            while starty > (drawing.height / 2) or starty < border:
                starty = random.randint(0, drawing.height)
            log.debug("drawing a %d leaf at %d,%d" % (aggregate, startx, starty))
            draw_leaf(drawing,startx,starty,rotate,aggregate / scale)

            #reset
            aggregate = 0
            minute = current_minute
        
    internal_state["minute"] = minute

    return None

def draw_leaf(drawing,x,y,rotate,width):
    leafsvg = drawing.load_svg("media/leaf.svg")
    leaf = leafsvg.getElementAt(1)
    th=TransformBuilder()
    th.setScaling( width ) 
    th.setRotation( rotate )
    th.setTranslation( "%d,%d" % ( x ,y ) )
    leaf.set_transform(th.getTransform())
    drawing.doc.addElement(leaf)

##all this stuff needs a bit of work, been hacked at mfuk
def begin(drawing,params,internal_state) :
    log.info("Starting tree with params: %s" % params)
    """
    internal_state["last_length"]= [0 for i in range(divs)]
    internal_state["last_div"]= 0
    internal_state["last_val"] = 0
    internal_state["start"] = 1
    """
    tree = drawing.load_svg("media/tree_init_500px.svg")
    #after importing, the svg has lost units. Original was 500 px wide, so now 500 units (in this case mm)
    tree_width = 500
    tr=TransformBuilder()
    width =  drawing.width / tree_width
    tr.setScaling( width ) 
    #have to add as a group, or pysvg adds a whole new svg into the drawing
    group = pysvg.structure.g()
    group.set_transform(tr.getTransform())

    for e in tree.getAllElements():
        group.addElement(e)
    drawing.doc.addElement(group)
    write_scale(drawing,params)
    
def end(drawing,params,internal_state) :
    pass
    #content="Ended at " + str(datetime.now())
    #drawing.bl_text(content,stroke="red",size=15)
    
def write_scale(drawing,params):
    draw_leaf(drawing,10,drawing.height - 100,0,1)
    #assume we get something every 5 minutes - wrong assumption but for now
    #the number we get in is in watts, eg 100 = 100W
    #so if scale is 100, 100W will result in leaf being scaled to 1(original  size)
    #so a full size leaf is equal in energy to 100W for 5min
    #typical is in hours, so divide by (60/5) 12 = 100/12 = 8.3wH
    #if it was 100W but scale is 50, then a full size leaf is 50W for 5 mins
    #so leaf is 50/20 = 2wH
    #so scale text is args.scale/12
    scale_text = "= %.1fWh" % ( params.get("value") / 12 )
    drawing.text(scale_text,50,drawing.height-60,20)

def get_params() :
    return  [ 
        #changing this needs to update the internal state, as we store an array of this number
        {"name":"value", "default":1, "description":"an input value of this will draw a leaf the same size as the scale leaf" },
        {"name":"interval", "default":10, "description":"how long (minutes) to wait before drawing a new leaf" },
# params can only be floats        {"name":"text", "default":'text', "description":"text for centre" },
            ]

def get_name() : return "Tree"
def get_description() : return "draws a tree, then leaves on the tree "

def can_run(data,params,internal_state):
    minute = int(internal_state.get("minute",0))
    interval = int(params.get("interval",10))
    for point in data.get_current():
        current_minute = get_minute(point.date) 
        if current_minute > minute + interval:
            log.info("leaf can run, %d > %d + %d" % (current_minute, minute, interval))
            return True
    log.info("leaf not running")
    return False

