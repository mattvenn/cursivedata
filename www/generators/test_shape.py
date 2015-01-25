import pysvg.text
import colorsys
from pysvg.builders import *

def process(drawing,data,params,internal_state) :
    print "Drawing an example rectangle",map(str,params)
    x = params.get('x')
    y = params.get('y')
    w = params.get('Width')
    h = params.get('Height')
    #drawing.rect(params.get('x'),params.get('y'),params.get('Width'),params.get('Height')) 
    drawing.path([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)])
    return None

def get_params() :
    return  [ 
             {"name":"Width", "default": 100, "description":"width in mm" },
             {"name":"Height", "default": 100, "description":"height in mm" }, 
             {"name":"x", "default": 0, "description":"x offset" },
             {"name":"y", "default": 0, "description":"y offset" }, ]

def get_name() : return "Shape Test"
def get_description() : return "Draw a square at the set position"

def begin(drawing,params,internal_state) :
    pass

def end(drawing,params,internal_state) :
    pass

def can_run(data,params,internal_state):
    return True
