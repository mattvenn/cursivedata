#!/usr/bin/python
import pickle
import sys
import math
import argparse
from pysvg.shape import *
from pysvg import parser
from pysvg.style import *
from pysvg.structure import svg
from pysvg.builders import *

def setup(args):
  widthmm = "%fmm" % args.width
  heightmm = "%fmm" % args.height

  dwg = svg(width=widthmm,height=heightmm)
  dwg.set_viewBox("0 0 %s %s" % (args.width, args.height))
  return dwg

def square(x,y, width,dwg,id):
  points = []
  hWidth = width/2
  #p = path("M%dmm,%dmm" % (x-hWidth,y-hWidth))
  sh=StyleBuilder()
  sh.setFilling('none')
  sh.setStroke('#000')
  sh.setStrokeWidth('0.1')

  p = path("M%d,%d" % (x-hWidth,y-hWidth),style=sh.getStyle())
  p.appendLineToPath(x+hWidth,y-hWidth,False)
  p.appendLineToPath(x+hWidth,y+hWidth,False)
  p.appendLineToPath(x-hWidth,y+hWidth,False)
  p.appendLineToPath(x-hWidth,y-hWidth,False)
  p.set_id(id)
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
      action='store', dest='value', type=int, default=5000,
      help="value of each square")
  argparser.add_argument('--squareIncMM',
      action='store', dest='squareIncMM', type=int, default=2,
      help="mm increase in size per square")
  argparser.add_argument('--load',
      action='store_const', const=True, dest='load', default=False,
      help="load values for env and number")
  argparser.add_argument('--nosavestate',
      action='store_const', const=False, dest='savestate', default=True,
      help="save state")
  argparser.add_argument('--drawoutline',
      action='store_const', const=True, dest='drawoutline', default=False,
      help="draw the outline of the square")


  args = argparser.parse_args()
  state = {}
  loadedvars = {} 

  if args.drawoutline:
    dwg = setup(args)
    square( args.width / 2,args.height/2, args.width, dwg )
    dwg.save()
    exit(0)

  if args.load:
    print "using numbers from file"
    loadedvars = pickle.load( open( "vars.p", "rb" ) )
    args.number = loadedvars["number"]
    args.env = loadedvars["env"]


  if args.savestate:
    print "using saved state"
    try:
      state = pickle.load( open( "save.p", "rb" ) )
    except:
      #duplicate code, avoid?
      state["number"] = args.number
      state["startenv"] = args.startenv
      state["id"] = 0
       
    #if we move on to a different number, set startenv back to 0
    if args.number != state["number"]:
      state["startenv"] = 0
      state["number"] = args.number
  else:
    state["number"] = args.number
    state["startenv"] = args.startenv
    state["id"] = 0

  print "number:%d\nstartenv:%d\nenv:%d" % (state["number"], state["startenv"], args.env)
  print "id:%d" % (state["id"])
  
  #work out where to draw
  import math
  startx = ( args.width / args.xdiv ) * (( state["number"] ) % args.xdiv ) + args.width / (args.xdiv * 2)
  starty = ( args.width / args.ydiv ) * math.ceil(state["number"] / args.ydiv ) + args.width / (args.ydiv * 2 )
 
  print "x:%d y:%d" % ( startx, starty )

  args.env += state["startenv"]
  startSquare = int(state["startenv"] / args.value)
  endSquare = int(args.env / args.value)
  print "start sq:%d end sq:%d" % ( startSquare, endSquare )

  #also update the concat
  try:
      concat = parser.parse("concat.svg")
#      print concat.getXML()
      print "parsed concat ok"
  except:
      print "problem parsing concat"
      concat = setup(args)

  if endSquare > startSquare:
    #create drawing
    dwg = setup(args)

    for i in range( startSquare, endSquare ):
      width = args.squareIncMM + i * args.squareIncMM
      print "square #%d width %d" % ( i, width )
      square( startx,starty, width, dwg, state["id"] )
      square( startx,starty, width, concat, state["id"] )
      state["id"] += 1

  dwg.save("square.svg")
  concat.save("concat.svg")

  state["startenv"] = args.env;
  pickle.dump( state, open( "save.p", "wb" ) )

  #pycam can do text natively!
  #dwg.add(dwg.text('Test', insert=(0, 0.2), fill='black'))

