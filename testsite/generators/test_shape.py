import pysvg.text
import colorsys
from pysvg.builders import *

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

def process(drawing,data,params,internal_state) :
    print "Drawing an example rectangle",map(str,params)
    drawing.rect(params.get('x'),params.get('y'),params.get('Width'),params.get('Height')) 
    return None

def get_params() :
    return  [ 
             {"name":"Width", "default": 200, "description":"width in mm" },
             {"name":"Height", "default": 200, "description":"height in mm" }, 
             {"name":"x", "default": 200, "description":"x offset" },
             {"name":"y", "default": 200, "description":"y offset" }, ]

def get_name() : return "Shape Test"
def get_description() : return "Draw a square at the set position"

def can_run(data,params,internal_state):
    return True
