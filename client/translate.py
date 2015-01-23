#!/usr/bin/python

import re
import argparse

parser = argparse.ArgumentParser(description="Translate GCode files to fit area")
parser.add_argument('--x-offset',
	action='store', dest='xoffset', type=float, default='0',
	help="X translation amount in mm")
parser.add_argument('--y-offset',
	action='store', dest='yoffset', type=float, default='0',
	help="Y translation amount in mm")
parser.add_argument('--input',
	action='store', dest='input', type=str, required=True,
	help="Input GCode file")
parser.add_argument('--output',
	action='store', dest='output', type=str, required=True,
	help="Output GCode file")

args = parser.parse_args()


infile = args.input
outfile = args.output
gcode = open(infile)
output = open(outfile,'w')
x_offset = args.xoffset
y_offset = args.yoffset

print "Transforming ", infile, " into ", outfile, " with xoffset ", x_offset, " and yoffset ", y_offset

gcodes = gcode.readlines()
gcode.close()

startCode = re.compile( "^g(.*),(.*)$")
vCode = re.compile( "^v(.*)$")

minx = 20000
miny = 20000
maxx = -20000
maxy = -20000
minv = 20000
maxv = -20000
for line in gcodes:
	s = startCode.match(line)
	v = vCode.match(line)
	if s:
		x = float(s.group(1)) + x_offset
		y = float(s.group(2)) + y_offset
		if x > maxx:
			maxx = x
		if x < minx:
			minx = x
		if y > maxy:
			maxy = y
		if y < miny:
			miny = y
		nv = "g" + format(x,'.1f') + "," + format(y,'.1f') + "\n"
		output.write(nv)
	elif v:
		vin = float(v.group(1))
		vo = vin/4 + 80
		if vo > maxv:
			maxv = vo
		if vo < minv:
			minv = vo
		nv = "v" + format(vo,'.0f') + "\n"
		output.write(nv)
	else:
		output.write(line)
output.close()
print "Ranges:"
print "X: ", minx, " to ", maxx
print "Y: ", miny, " to ", maxy
print "V: ", minv, " to ", maxv


