#!/usr/bin/python
import argparse
import re
import sys

def parse(args):
  try:
    gcode = open( args.file )
  except:
    print "bad file"
    exit( 1 )
  

  #start the file
  #print "p3,100"
  #print "c"

  xmin = 100000
  xmax = 0
  ymin = 100000
  ymax = 0

  gcodes = gcode.readlines()
  startCode = re.compile( "^G([01])(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
  contCode =  re.compile( "^(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
  polar_code=""
  #p = re.compile( "G([01])(?= Z(\S+))")
  for line in gcodes:
    s = startCode.match(line)
    c = contCode.match(line)
    gcode = 0
    if s:
      gcode = s.group(1)
      x = s.group(2)
      y = s.group(3)
      z = float(s.group(4))
      if z > 0 :
        #don't draw
        polar_code += "d0\n"
      else:
        #draw
        polar_code += "d1\n"
    elif c: 
      try:
        x = float(c.group(1))
      except:
        x = lastX 
      try:
        y = float(c.group(2))
      except:
        y = lastY
  #    z = float(c.group(3))
  #    print line
      outx = x*args.scale+args.xoffset
      outy = args.ysub - y*args.scale+args.yoffset
      polar_code += "g%d,%d\n" %  (outx,outy) 
      lastX = x
      lastY = y
      if outx < xmin:
        xmin = outx 
      if outx > xmax:
        xmax = outx
      if outy < ymin:
        ymin = outy
      if outy > ymax:
        ymax = outy

  if args.showminmax:
    polar_code += "# xmin %f xmax %f\n" % (xmin, xmax)
    polar_code += "# ymin %f ymax %f\n" % (ymin, ymax)

  gcodes = len(polar_code.splitlines())
  total_lines = gcodes

  if args.force_store:
    total_lines+=3

  if total_lines>=15:
    #too long for the robot!
    print >> sys.stderr, "too many gcodes for the robot"
    exit(1)

  if args.force_store:
    print "s%d,0" % gcodes
  print polar_code,
  if args.force_store:
    print "s%d,0\ne%d,0" % (gcodes,gcodes)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="preprocesses ngc files for polargraph robot")
    parser.add_argument('--file',
        action='store', dest='file', 
        help="file to open")
    parser.add_argument('--scale',
        action='store', dest='scale', type=float, default=5.0,
        help="scale factor")
    parser.add_argument('--ysub',
        action='store', dest='ysub', type=int, default=1500,
        help="need to reflect y axis atm, this is what the y is subtracted from. should be a bit bigger than maximum y")
    parser.add_argument('--yoffset',
        action='store', dest='yoffset', type=int, default=400,
        help="how far to move the file on y axis")
    parser.add_argument('--xoffset',
        action='store', dest='xoffset', type=int, default=1200,
        help="how far to move the file on x axis")
    parser.add_argument('--showminmax',
        action='store_const', const=True, dest='showminmax', default=False,
        help="show the min and max xy after scaling")
    parser.add_argument('--force_store',
        action='store_const', const=True, dest='force_store', default=False,
        help="forces the robot to store the drawing before doing it")

    args = parser.parse_args()

    #set values, must be a better way of doing this
    parse(args)
