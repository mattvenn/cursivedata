#!/usr/bin/python
"""
bugs:
"""

import random
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

def processData(json):
    data = []
    minMin = 1500
    maxMin = 0
    for d in json:
        date = iso8601.parse_date(d["at"])
        minute = int( date.strftime("%M") ) # minute 0 -59
        hour = int(date.strftime("%H") ) # hour 0 -23
        mins =  (minute + hour * 60)/10 # 0 - 143
        if mins < minMin:
            minMin = mins
        if mins > maxMin:
            maxMin = mins
        light = d["value"]
        data.append((mins,light))
    global args
    if args.debug:
        print "parsed %d lines" % len(data)
        print "min mins: %d max mins: %d" % ( minMin ,maxMin )
    return data

def setup(args):
  widthmm = "%fmm" % args.width
  heightmm = "%fmm" % args.height

  dwg = svg(width=widthmm,height=heightmm)
  dwg.set_viewBox("0 0 %s %s" % (args.width, args.height))
  return dwg


def leaf(x,y,width,dwg,id,args):
  leafsvg = parser.parse(args.dir + "leaf.svg")
  leaf = leafsvg.getElementAt(1)
  rotate = random.randint(0,360)
  th=TransformBuilder()
  th.setScaling( width ) 
  th.setRotation( rotate)
  th.setTranslation( "%d,%d" % ( x ,y ) )
  leaf.set_transform(th.getTransform())
  leaf.set_id(id)
  dwg.addElement(leaf)


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
  """
  argparser.add_argument('--value',
      action='store', dest='value', type=int, default=5000,
      help="value of each square")
  """
  argparser.add_argument('--scale',
      action='store', dest='scale', type=float, default=100,
      help="divide data total by this number to get svg scale amount")
  argparser.add_argument('--dir',
      action='store', dest='dir', default="./",
      help="directory for files")
  argparser.add_argument('--wipe',
      action='store_const', const=True, dest='wipe', default=False,
      help="start with a new tree")
  argparser.add_argument('--load',
      action='store_const', const=True, dest='load', default=False,
      help="load values for env and number")
  argparser.add_argument('--debug',
      action='store_const', const=True, dest='debug', default=False,
      help="debug print")
  argparser.add_argument('--drawnow',
      action='store_const', const=True, dest='drawnow', default=False,
      help="draw a leaf of given size immediately")
  argparser.add_argument('--drawoutline',
      action='store_const', const=True, dest='drawoutline', default=False,
      help="draw the outline of the square")
  argparser.add_argument('--loadhistory',
      action='store', dest='loadhistory', default=None,
      help="load a history file")


  args = argparser.parse_args()
  state = {}
  loadedvars = {} 

  if args.wipe:
    print "wiping"
    fromfile = open(args.dir + "tree_init.svg",'r')
    tofile = open(args.dir + "tree.svg",'w')
    tofile.write(fromfile.read())
    tofile.close()
    fromfile.close()

  if args.load:
    print "using numbers from file"
    loadedvars = pickle.load( open( args.dir + vars.p, "rb" ) )
    args.number = loadedvars["number"]
    args.env = loadedvars["env"]

  #create drawing
  dwg = setup(args)

  #also setup concat drawing
  try:
      concat = parser.parse(args.dir + "tree.svg")
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
       
    #prepare the array, only one datum which is for now
    data = []
    data.append((args.number,args.env))

  newfile = False #exit status depends on if we write a new file
  for datum in data:
      value = int(float(datum[1])) #the value of the datum
      last_number = state["number"] #last datum's minute
      state["number"]=int(datum[0]) #this datum's minute
      if args.debug:
        print "last number: %d, number: %d, value: %d" % ( last_number, state["number"], value )

      if last_number != state["number"] or args.drawnow: #if move onto next minute

        scale = float(state["startenv"]) / args.scale 
        if args.debug:
            print "total for %d was %d" % (last_number, state["startenv"])
            print "scale %f" % scale
        state["startenv"] = 0

        #work out where to draw
        border = args.width / 10
        startx = 0
        starty = 0
        startx =  random.randint(border, args.width-border)
        while starty > (args.height / 2) or starty < border:
          starty = random.randint(0, args.height)

        if not args.loadhistory:
            leaf( startx,starty, scale, dwg, last_number,args )
            dwg.save(args.dir + "leaf_frame.svg")
        leaf( startx,starty, scale, concat, last_number,args )
        newfile = True

      state["startenv"] += value

  concat.save(args.dir + "tree.svg")

  pickle.dump( state, open( args.dir + "save.p", "wb" ) )

  #pycam can do text natively!
  #dwg.add(dwg.text('Test', insert=(0, 0.2), fill='black'))
  if newfile:
    exit(0)
  exit(1)
