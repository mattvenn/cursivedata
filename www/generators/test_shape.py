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
    colour = internal_state.get("colour",0)
    rotate = internal_state.get("rotate",0)
    x = params.get('x')
    y = params.get('y')
    for point in data.get_current():
        if point.getStreamName() == params.get('colourid'):
            print("colour = %f" %  point.getValue())
            internal_state["colour"]= point.getValue()
        elif point.getStreamName() == params.get('rotateid'):
            print("rotate = %f" % point.getValue())
            internal_state["rotate"]= point.getValue()
    transform = "rotate(%d,%d,%d)" % (rotate,x,y)
    colour = 'rgb({0},{0},{0})'.format(colour)

    print "Drawing an example rectangle",map(str,params)
    drawing.rect(x,y,params.get('Width'),params.get('Height'),transform=transform,fill=colour) 
    return None

def get_params() :
    return  [ 
             {"name":"Width", "default": 100, "description":"width in mm" },
             {"name":"Height", "default": 100, "description":"height in mm" }, 
             {"name":"x", "default": 0, "description":"x offset" },
             {"name":"y", "default": 0, "description":"y offset" }, 
             {"name":"colourid", "default": 0, "description":"which source ID for colour", 'data_type':"text" }, 
             {"name":"rotateid", "default": 1, "description":"which source ID for rotation", 'data_type':"text" }, ]

def get_name() : return "Shape Test"
def get_description() : return "Draw a square at the set position"

def can_run(data,params,internal_state):
    return True
