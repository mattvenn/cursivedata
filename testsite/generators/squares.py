"""
bugs:
  with squareIncMM an odd number, the squares don't join up properly...
"""
import pysvg.text
from pysvg.shape import *
#from pysvg.style import *
from pysvg.builders import *

import datetime
import math

def square(x,y,width,dwg,id,rotate):
  points = []
  hWidth = width/2
  style_dict = { "fill":"none", "stroke":"#000", "stroke-width":"1" }

  p = path("M%d,%d" % (x-hWidth,y-hWidth))
  p.appendLineToPath(x+hWidth,y-hWidth,False)
  p.appendLineToPath(x+hWidth,y+hWidth,False)
  p.appendLineToPath(x-hWidth,y+hWidth,False)
  p.appendLineToPath(x-hWidth,y-hWidth,False)
  p.set_style(StyleBuilder(style_dict).getStyle())
  p.set_id(id)
  if rotate:
    p.set_transform("rotate(%d,%d,%d)" % (rotate,x,y))
  dwg.addElement(p)

def get_minute(date):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    mins =  (minute + hour * 60)/10 # 0 - 143
    return mins

def process(svg_document,data,params,internal_state) :

    aggregate = internal_state.get("aggregate",0)
    square_num = int(internal_state.get("square_num",0))
    xdiv = params.get("Xdiv")
    ydiv = params.get("Ydiv")

    for point in data.get_current():
      aggregate += float(point['value'])
      #allow user to determine how fast the graph is drawn again
      number = get_minute(point['time'])
      #work out where to draw
      cell_width = params.get("Width") / xdiv
      cell_height = params.get("Height") / ydiv
      startx = (number % xdiv) * cell_width
      starty = math.ceil(number / ydiv) * cell_height
      startx += cell_width / 2
      starty += cell_height / 2
      #if we move to a new cell, start small again
      if startx != internal_state.get("last_x",0) or starty != internal_state.get("last_y",0):
          internal_state["last_x"] = startx
          internal_state["last_y"] = starty
          print "reset square num"
          square_num = 0
        
      print "number:%d\naggregate:%.2f" % (number, aggregate)
      print "x:%d y:%d" % ( startx, starty )

      #if we have aggregated enough values to draw a square
      while aggregate > params.get("Value"):
          width = params.get("SquareInc") + square_num * params.get("SquareInc")
          print "square #%d width %d" % ( square_num, width )
          if params.get("Rotate"):
            rotate = int(square_num*params.get("Rotate")) % 360 
          else:
            rotate = 0
          square( startx,starty,width,svg_document,number,rotate)
          aggregate -= params.get("Value")
          #increment squares
          square_num += 1

    internal_state["aggregate"]=aggregate
    internal_state["square_num"]=square_num
    return None
      
def get_params() :
    return  [ 
        {"name":"Width", "default": 200, "description":"width in mm" },
        {"name":"Height", "default": 200, "description":"height in mm" }, 
        {"name":"Ydiv", "default": 12, "description":"divide paper into y divs" },
        {"name":"Xdiv", "default": 12, "description":"divide paper into x divs" },
        {"name":"SquareInc", "default":2, "description":"amount subsequent squares increase in size" },
        {"name":"Rotate", "default":0, "description":"rotate degrees" },
        {"name":"Value", "default":3000, "description":"value of each square" },
            ]

def get_name() : return "Squares"
def get_description() : return "every 10 minutes start drawing squares about a common point. Each square is worth a certain value. Subsequent squares are drawn larger, and can be rotated"

def can_run(data,params,internal_state):
    #run every time
    return len(data.get_current()) >= 1

