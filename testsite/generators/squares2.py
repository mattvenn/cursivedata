import datetime
import pickle
import math
import sys
import math
import argparse
import json
from xml.dom import Node
from pysvg.core import TextContent
from pysvg.shape import *
from pysvg import parser
from pysvg.style import *
from pysvg.structure import svg
from pysvg.builders import *
import iso8601

def setup(state):
  widthmm = "%fmm" % state.get_param("width")
  heightmm = "%fmm" % state.get_param("height")

  dwg = svg(width=widthmm,height=heightmm)
  dwg.set_viewBox("0 0 %s %s" % (args.width, args.height))
  return dwg



def process(data,params,state=None) :
    state = state or {}
    #print "Example Processing data with",map(str,state.generatorstateparameter_set.all())
    for datum in data:
        print datum
        value = int(float(datum[1])) #Used to be params[env]
        number=int(datum[0]) #should be state["number"]
        startnum = 0 # should be state["startnum"]

        last_number = state["number"]
        state["number"]=int(datum[0])
        if last_number != state["number"]:
            #reset
            state["startenv"] = 0

        #work out where to draw
        startx = ( params["width"] / params["xdiv"] ) * (( number ) % params["xdiv"] ) + params["width"] / (params["xdiv"] * 2)
        starty = ( params["width"] / params["ydiv"] ) * math.ceil(number / params["ydiv"] ) + params["width"] / (params["ydiv"] * 2 )

        value += startnum
        startSquare = int(startnum / params["value"])
        endSquare = int(value / params["value"])

        id = state["number"]
        startid = 0
        #writeJSVars(id + 1, startid)

    #if params["debug"]:
         #print "number:%d\nstartenv:%d\nenv:%d" % (state["number"], state["startenv"], params[env])
         #print "id:%s" % (id)
         #print "x:%d y:%d" % ( startx, starty )
         #print "start sq:%d end sq:%d" % ( startSquare, endSquare )

    if endSquare > startSquare:
      for i in range( startSquare, endSquare ):
         width = params["squareIncMM"] + i * params["squareIncMM"]
         print "square #%d width %d" % ( i, width )
         newfile = True
         if not state["loadhistory"]:
              square( startx,starty, width, dwg, id,params,False )
         square( startx,starty, width, concat, id,params, False )

      if not state["loadhistory"]:
         dwg.save(state["dir"] + "square.svg")
    
    state["startenv"] = state.get("env")
    #return dwg
    return "Done!"



def get_params() :
    return  [ 
    { "name":"width", "default":"300" }, 
    { "name":"height", "default":"300" } ,
    { "name":"startenv", "default":"300" } ,
    { "name":"xdiv", "default":"3" } ,
    { "name":"ydiv", "default":"3" } ,
    { "name":"value", "default":"300" } ,
    { "name":"rotate", "default":"2" } ,
    { "name":"squareIncMM", "default":"300" } ,
    { "name":"drawoutline", "default":"300" } ,
    ]


def get_name() : return "Squares Generator"
def get_description() : return "Uses squares to plot stuff varying size based on some variable"



def square(x,y, width,dwg,id,args,hidden):
    print "Drawing square",str(x),y,width,dwg
    points = []
    hWidth = width/2
    #p = path("M%dmm,%dmm" % (x-hWidth,y-hWidth))
    style_dict = { "fill":"none", "stroke":"#000", "stroke-width":"0.1" }
    if hidden:
        style_dict["display"]="none"

    p = path("M%d,%d" % (x-hWidth,y-hWidth))
    p.appendLineToPath(x+hWidth,y-hWidth,False)
    p.appendLineToPath(x+hWidth,y+hWidth,False)
    p.appendLineToPath(x-hWidth,y+hWidth,False)
    p.appendLineToPath(x-hWidth,y-hWidth,False)
    p.set_style(StyleBuilder(style_dict).getStyle())
    p.set_id(id)
    if args.rotate:
        p.set_transform("rotate(%d,%d,%d)" % ((int(id)*args.rotate) % 360 ,x,y))
    #group.addElement(p)
    #dwg.addElement(group)
    dwg.addElement(p)

