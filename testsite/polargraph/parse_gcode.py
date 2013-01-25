import re


def parse(endpoint,generator_params,infile,outfile):

  try:
    gcode = open(infile)
  except:
    print "bad file"
    exit( 1 )
  xmin = 0
  ymin = 0
  #these should be validated as floats somewhere
  xmax = float(generator_params.get("Width"))
  ymax = float(generator_params.get("Height"))

  gcodes = gcode.readlines()

  available_x = endpoint.width - endpoint.side_margin * 2
  if float(xmax) > available_x:
    print "gcodes x too large for robot"
    exit(1)

  available_y = endpoint.height - endpoint.top_margin
  if ymax > available_y:
    print "gcodes y too large for robot"
    exit(1)

  #hack for centering for now
  xoffset = endpoint.width/2 - xmax/2
  yoffset = endpoint.height/2 - ymax/2
  if yoffset < endpoint.top_margin:
    yoffset = endpoint.top_margin

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

  """
  if args.showminmax:
    polar_code += "# xmin %f xmax %f\n" % (xmin, xmax)
    polar_code += "# ymin %f ymax %f\n" % (ymin, ymax)
  gcodes = len(polar_code.splitlines())
  total_lines = gcodes
  """

  file = open(outfile,"w")
  print "writing polar file to ", outfile
  file.write(polar_code)
