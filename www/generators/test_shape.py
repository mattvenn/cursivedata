import pysvg.text
import colorsys
from pysvg.builders import *

import logging
log = logging.getLogger('generator')

#Not used now. Left for posterity and how to do paths
def square(x,y,width,height,dwg):
    style_dict = { "fill":"none", "stroke":"#000", "stroke-width":"1" }
    p = path("M%d,%d" % (x,y))
    p.appendLineToPath(x+width,y,False)
    p.appendLineToPath(x+width,y+height,False)
    p.appendLineToPath(x,y+width,False)
    p.appendLineToPath(x,y,False)
    p.set_style(StyleBuilder(style_dict).getStyle())
    p.set_id(id)
    dwg.addElement(p)

def begin(drawing,params,internal_state) :
    drawing.rect(0,0,drawing.width,drawing.height) 
    
def end(drawing,params,internal_state) :
    pass
    

def process(drawing,data,params,internal_state) :
    colour = internal_state.get("colour",0)
    rotate = internal_state.get("rotate",0)
    x = params.get('x')
    y = params.get('y')
    for point in data.get_current():
        if point.getStreamName() == params.get('colourid'):
            log.debug("colour = %f" %  point.getValue())
            colour = point.getValue()
        elif point.getStreamName() == params.get('rotateid'):
            log.debug("rotate = %f" % point.getValue())
            rotate = point.getValue()
        else:
            colour = 0
            rotate = 0

    transform = "rotate(%d,%d,%d)" % (rotate,x,y)
    colour = 'rgb({0},{0},{0})'.format(colour)

    log.debug("Drawing an example rectangle with params: %s" % params)
    drawing.rect(x,y,params.get('Width'),params.get('Height'),transform=transform,fill=colour) 

    internal_state["colour"] = colour
    internal_state["rotate"] = rotate

    return None

def get_params() :
    return  [ 
             {"name":"Width", "default": 100, "description":"width in mm" },
             {"name":"Height", "default": 100, "description":"height in mm" }, 
             {"name":"x", "default": 0, "description":"x offset" },
             {"name":"y", "default": 0, "description":"y offset" }, 
             {"name":"colourid", "default": 0, "description":"which source name for colour", 'data_type':"text" }, 
             {"name":"rotateid", "default": 1, "description":"which source name for rotation", 'data_type':"text" }, ]

def get_name() : return "Shape Test"
def get_description() : return "Draw a square at the set position"

def can_run(data,params,internal_state):
    return True
