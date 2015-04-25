#!/usr/bin/python

import re
import argparse

import pysvg.structure
from cursivelib.robot_spec import *
from cursivelib.robot_spec import string_to_spec
from cursivelib.svg_to_gcode import *
from cursivelib.gcode import *
from cursivelib.pycam_gcode import *
import cursivelib.svg as svg
import pysvg.text as txt

from cursivelib.robot_spec import add_botspec_arguments
from cursivelib.robot_spec import get_botspec_from_args










parser = argparse.ArgumentParser(description="Translate GCode to SVG for checking")
add_botspec_arguments(parser)
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
parser.add_argument('--pen-size',
	action='store', dest='pen_size', type=float, default="0.2",
	help="Width of line drawn with pen commands")
parser.add_argument('--pen-color',
	action='store', dest='pen_color', type=str, default="rgb(255,100,100)",
	help="Color of line drawn with pen commands")
parser.add_argument('--font-size',
	action='store', dest='font_size', type=float, default=20,
	help="Font size for box coordinates")

args = parser.parse_args()
# Specifications of the robot which will do the drawing
robot_spec = get_botspec_from_args(args)



min_dwell = args.min_dwell
max_dwell = args.max_dwell
drill_size = args.drill_size

infile = args.input
outfile = args.output

converter = GcodeToSVG(robot_spec,
        min_dwell=args.min_dwell,
        max_dwell=args.max_dwell,
        drill_size = args.drill_size,
        dwell_fill = args.dwell_fill,
        pen_size= args.pen_size,
        pen_color = args.pen_color,
        font_size = args.font_size
        )
converter.convert(infile,outfile)
