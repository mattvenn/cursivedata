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

  #assume, could fix when we sort out the below
  xmin = 0
  ymin = 0
  xmax = args.width
  ymax = args.height

  gcodes = gcode.readlines()
  """ doesn't work because min and max are for each animation frame
  try:
    xmax = float(re.search(r'^;maxx = (\S+)$',"".join(gcodes),re.MULTILINE).group(1))
    xmin = float(re.search(r'^;minx = (\S+)$',"".join(gcodes),re.MULTILINE).group(1))
    ymax = float(re.search(r'^;maxy = (\S+)$',"".join(gcodes),re.MULTILINE).group(1))
    ymin = float(re.search(r'^;miny = (\S+)$',"".join(gcodes),re.MULTILINE).group(1))
  except AttributeError, e:
    print "couldn't find min and max x and y in file, aborting!"
    exit(1)
  """
  available_x = args.robot_width - args.side_margin * 2
  if float(xmax) > available_x:
    print "gcodes x too large for robot"
    exit(1)

  available_y = args.robot_height - args.top_margin
  if ymax > available_y:
    print "gcodes y too large for robot"
    exit(1)

  xoffset = (available_x - xmax) / 2 + args.side_margin
  yoffset = args.top_margin

  startCode = re.compile( "^G([01])(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
  contCode =  re.compile( "^(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
  
  polar_code=""
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

      outx = x+xoffset
      outy = ymax-y+yoffset #flip y because pycam outputs with 0,0 in the bottom left, but the robot's 0,0 is the top left
      polar_code += "g%.1f,%.1f\n" %  (outx,outy) 
#      polar_code += "g%d,%d\n" %  (outx,outy) 
      lastX = x
      lastY = y

  if args.showminmax:
    polar_code += "# xmin %f xmax %f\n" % (xmin, xmax)
    polar_code += "# ymin %f ymax %f\n" % (ymin, ymax)

  gcodes = len(polar_code.splitlines())
  total_lines = gcodes

  if args.force_store:
    total_lines+=3
  """
  if total_lines>=15:
    #too long for the robot!
    print >> sys.stderr, "too many gcodes for the robot"
    exit(1)
  """
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
        action='store', dest='scale', type=float, default=1.0,
        help="scale factor")
    parser.add_argument('--width',
        action='store', dest='width', type=int, default=200,
        help="width of the whole drawing")
    parser.add_argument('--height',
        action='store', dest='height', type=int, default=200,
        help="height of the whole drawing")
    parser.add_argument('--top-margin',
        action='store', dest='top_margin', type=int, default=100,
        help="top margin of the robot in mm")
    parser.add_argument('--side-margin',
        action='store', dest='side_margin', type=int, default=100,
        help="side margin of the robot in mm")
    parser.add_argument('--robot-width',
        action='store', dest='robot_width', type=int, default=500,
        help="width of the robot in mm")
    parser.add_argument('--robot-height',
        action='store', dest='robot_height', type=int, default=300,
        help="height of the robot in mm")
    parser.add_argument('--showminmax',
        action='store_const', const=True, dest='showminmax', default=False,
        help="show the min and max xy after scaling")
    parser.add_argument('--force_store',
        action='store_const', const=True, dest='force_store', default=False,
        help="forces the robot to store the drawing before doing it")

    args = parser.parse_args()

    #set values, must be a better way of doing this
    parse(args)
