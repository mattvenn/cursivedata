#!/usr/bin/env python
"""
bugs:
  with squareIncMM an odd number, the squares don't join up properly...
"""
import datetime
import pickle
import math
import sys
import math
import argparse
import json
from pysvg.shape import *
from pysvg import parser
from pysvg.style import *
from pysvg.structure import svg
from pysvg.builders import *
import iso8601

def writeJSVars(id,startid):
    fh = open( args.dir + "vars.js", 'w' )
    fh.write( "var min = %s; var max = %s;" % (startid, id ))
    fh.close()

def processData(json):
    data = []
    for d in json:
        if len(data) > 10000:
            break
        date = iso8601.parse_date(d["at"])
        minute = int( date.strftime("%M") ) # minute 0 -59
        hour = int(date.strftime("%H") ) # hour 0 -23
        mins =  (minute + hour * 60)/10 # 0 - 143
        light = d["value"]
        data.append((mins,light))
    return data

def setup(args):
  widthmm = "%fmm" % args.width
  heightmm = "%fmm" % args.height

  dwg = svg(width=widthmm,height=heightmm)
  dwg.set_viewBox("0 0 %s %s" % (args.width, args.height))
  return dwg

def square(x,y, width,dwg,id,args,hidden):
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


if __name__ == '__main__':
  argparser = argparse.ArgumentParser(
      description="generates square based energy drawings")
  argparser.add_argument('--height',
      action='store', dest='height', type=int, default=200,
      help="height of paper")
  argparser.add_argument('--width',
      action='store', dest='width', type=int, default=200,
      help="width of paper")
  argparser.add_argument('--startenv',
      action='store', dest='startenv', type=int, default=0,
      help="where to start from")
  argparser.add_argument('--number',
      action='store', dest='number', type=int, default=0,
      help="will end up being the time")
  argparser.add_argument('--env',
      action='store', dest='env', type=int, default=0,
      help="environmental var to plot")
  argparser.add_argument('--xdiv',
      action='store', dest='xdiv', type=int, default=12,
      help="divide paper into x divs")
  argparser.add_argument('--ydiv',
      action='store', dest='ydiv', type=int, default=12,
      help="divide paper into y divs")
  argparser.add_argument('--value',
      action='store', dest='value', type=int, default=3000,
      help="value of each square")
  argparser.add_argument('--rotate',
      action='store', dest='rotate', type=int, default=0,
      help="degrees to rotate * the shape's id")
  argparser.add_argument('--squareIncMM',
      action='store', dest='squareIncMM', type=float, default=2,
      help="mm increase in size per square")
  argparser.add_argument('--load',
      action='store_const', const=True, dest='load', default=False,
      help="load values for env and number")
  argparser.add_argument('--debug',
      action='store_const', const=True, dest='debug', default=False,
      help="debug print")
  argparser.add_argument('--drawoutline',
      action='store_const', const=True, dest='drawoutline', default=False,
      help="draw the outline of the square")
  argparser.add_argument('--loadhistory',
      action='store', dest='loadhistory', default=None,
      help="load a history file")
  argparser.add_argument('--dir',
      action='store', dest='dir', default="./",
      help="directory for files")


  args = argparser.parse_args()
  state = {}
  loadedvars = {} 


  if args.load:
    print "using numbers from file"
    loadedvars = pickle.load( open( args.dir + "vars.p", "rb" ) )
    args.number = loadedvars["number"]
    args.env = loadedvars["env"]

  #create drawing
  dwg = setup(args)

  #also setup concat drawing
  try:
      concat = parser.parse(args.dir + "concat.svg")
      if args.debug:
        print "parsed concat ok"
  except:
      if args.debug:
        print "problem parsing concat"
      concat = setup(args)

  #draw outline square
  if args.drawoutline:
    dwg = setup(args)
    square( args.width / 2,args.height/2, args.width, dwg )
    dwg.save()
    exit(0)

  #2 different things can happen here, either we are loading a whole load of points at once, or we are running realtime
  #load of points at once
  if args.loadhistory:
    try:
        fh = open(args.dir + args.loadhistory)
        jsondata = json.load(fh)
        data=processData(jsondata)
        state["startenv"] = 0
        state["number"] = 0

    except:
        "failed to read history file"
        exit(1)
  else:
    try:
      state = pickle.load( open( args.dir + "save.p", "rb" ) )
      #will throw an exception if not available
    except:
      print "exception loading state, creating default state"
      state["startenv"] = args.startenv
      state["number"] = args.number
       
    #if we move on to a different number, set startenv back to 0
    if args.number != state["number"]:
      state["startenv"] = 0
      state["number"] = args.number

    #prepare the array, only one datum which is for now
    data = []
    data.append((state["number"],args.env))

  newfile = False #exit status depends on if we write a new file
  for datum in data:
      args.env = int(float(datum[1]))
      last_number = state["number"]
      state["number"]=int(datum[0])
      if last_number != state["number"]:
        #reset
        state["startenv"] = 0
  
      #work out where to draw
      startx = ( args.width / args.xdiv ) * (( state["number"] ) % args.xdiv ) + args.width / (args.xdiv * 2)
      starty = ( args.width / args.ydiv ) * math.ceil(state["number"] / args.ydiv ) + args.width / (args.ydiv * 2 )
 
      args.env += state["startenv"]
      startSquare = int(state["startenv"] / args.value)
      endSquare = int(args.env / args.value)

      now = datetime.datetime.now()
      start_date = now - datetime.timedelta(hours=12)
      id = now.strftime("%s")
      startid = start_date.strftime("%s")
      writeJSVars(id,startid)

      if args.debug:
          print "number:%d\nstartenv:%d\nenv:%d" % (state["number"], state["startenv"], args.env)
          print "id:%s" % (id)
          print "x:%d y:%d" % ( startx, starty )
          print "start sq:%d end sq:%d" % ( startSquare, endSquare )

      if endSquare > startSquare:
        for i in range( startSquare, endSquare ):
          width = args.squareIncMM + i * args.squareIncMM
          print "square #%d width %d" % ( i, width )
          newfile = True
          if not args.loadhistory:
              square( startx,starty, width, dwg, id,args,False )
          square( startx,starty, width, concat, id,args,True )

        if not args.loadhistory:
          dwg.save(args.dir + "square.svg")
      
      state["startenv"] = args.env

  concat.save(args.dir + "concat.svg")

  state["startenv"] = args.env;
  pickle.dump( state, open( args.dir + "save.p", "wb" ) )

  #pycam can do text natively!
  #dwg.add(dwg.text('Test', insert=(0, 0.2), fill='black'))
  if newfile:
    exit(0)
  exit(1)
