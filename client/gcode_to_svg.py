#!/usr/bin/python

import re
import argparse

import pysvg.structure
from cursivelib.robot_spec import *
from cursivelib.robot_spec import string_to_spec
from cursivelib.svg_to_gcode import *
from cursivelib.pycam_gcode import *
import cursivelib.svg as svg
import pysvg.text as txt



def dwell_prop(d) :
	if d > max_dwell:
		return 1
	if d < min_dwell:
		return 0
	return (d - min_dwell) / (max_dwell - min_dwell)

def add_rect(x,y,width,height,stroke="rgb(0,0,0)",fill="none",strokewidth=9,font_size=80.0,inside=True,outside=False) :
	tlx = x;
	tly = y;
	brx = x+width;
	bry = y+height;
	mrg = font_size/4
	tls = str(tlx)+", "+str(tly)
	brs = str(brx)+", "+str(bry)
	bo = font_size * float(len(brs)) / 2
	doc.addElement(build.createRect(x, y, width=width, height=height, stroke=stroke, strokewidth=strokewidth,fill=fill))
	if inside:
		doc.addElement(txt.text(content=tls,x=tlx+mrg,y=tly+5*mrg,	fill=stroke,font_size=font_size))
		doc.addElement(txt.text(content=brs,x=brx+mrg-bo,y=bry-mrg,	fill=stroke,font_size=font_size))
	if outside:
		doc.addElement(txt.text(content=tls,x=tlx+mrg,y=tly-mrg,	fill=stroke,font_size=font_size))
		doc.addElement(txt.text(content=brs,x=brx+mrg-bo,y=bry+5*mrg,	fill=stroke,font_size=font_size))



parser = argparse.ArgumentParser(description="Translate GCode to SVG for checking")
parser.add_argument('--bot-spec',
	action='store', dest='botspec', type=str, required=True,
	help="Robot spec as height, width, top_margin, side_margin")
parser.add_argument('--input',
	action='store', dest='input', type=str, required=True,
	help="Input GCode file")
parser.add_argument('--output',
	action='store', dest='output', type=str, required=True,
	help="Output SVG file")
parser.add_argument('--min-dwell',
	action='store', dest='min_dwell', type=float, default=80.0,
	help="Minimum dwell range (for size 0 circle)")
parser.add_argument('--max-dwell',
	action='store', dest='max_dwell', type=float, default=240.0,
	help="Maximum dwell range (for size <drill_size> circle)")
parser.add_argument('--drill-size',
	action='store', dest='drill_size', type=float, default=50.0,
	help="Drill size (circles with maximum dwell)")
parser.add_argument('--dwell-fill',
	action='store', dest='dwell_fill', type=str, default="rgb(255,230,210)",
	help="Fill for circles drawn when dwelling (e.g. spraycans)")
parser.add_argument('--draw-width',
	action='store', dest='draw_width', type=float, default="4",
	help="Width of line drawn with pen commands")
parser.add_argument('--draw-stroke',
	action='store', dest='draw_stroke', type=str, default="rgb(255,100,100)",
	help="Color of line drawn with pen commands")

args = parser.parse_args()



min_dwell = args.min_dwell
max_dwell = args.max_dwell
drill_size = args.drill_size

infile = args.input
outfile = args.output
gcode = open(infile)
robot=string_to_spec(args.botspec)

build = pysvg.builders.ShapeBuilder()
doc = pysvg.structure.svg(width=robot.width,height=robot.height)

gcodes = gcode.readlines()
gcode.close()

moveCode = re.compile( "^g(.*),(.*)$")
penCode = re.compile( "^d(.*)$")
dwellCode = re.compile( "^v(.*)$")



pen = 0
stroke_width = 10

add_rect(0, 0, robot.width, robot.height, stroke="rgb(200,200,150)", strokewidth=9,fill="rgb(255,255,240)",outside=True)
add_rect(robot.x_min, robot.y_min, robot.img_width, robot.img_height, 
	stroke = "rgb(100, 255, 100)", strokewidth=9, fill="rgb(240,255,240)")

x = 0
y = 0

minx = 20000
miny = 20000
maxx = -20000
maxy = -20000
minv = 20000
maxv = -20000
for line in gcodes:
	move = moveCode.match(line)
	dwell = dwellCode.match(line)
	pen_cmd = penCode.match(line)
	if move:
		xnew = float(move.group(1))
		ynew = float(move.group(2))
		if xnew > maxx:
			maxx = xnew
		if xnew < minx:
			minx = xnew
		if ynew > maxy:
			maxy = ynew
		if ynew < miny:
			miny = ynew
		if pen:
			doc.addElement(build.createLine(x,y,xnew,ynew,strokewidth=args.draw_width,stroke=args.draw_stroke))
		x = xnew
		y = ynew
	elif pen_cmd:
		pen_height = int(pen_cmd.group(1))
		print "Pen: ", pen_height
		pen = pen_height
	elif dwell and pen:
		dwell_time = float(dwell.group(1))
		print "Dwell: ", dwell_time
		drill_amt = drill_size * dwell_prop(dwell_time)
		print "Amt: ", drill_amt
		print "Adding circle of size ",drill_amt," at ", x, ", ",y
		doc.addElement(build.createCircle(x, y, r=drill_amt, fill = args.dwell_fill,stroke="none"))
	else:
		pass


add_rect(minx, miny, width=maxx-minx, height=maxy-miny, stroke="rgb(128,128,128)", strokewidth=6,inside=False,outside=True)
doc.save(outfile)





