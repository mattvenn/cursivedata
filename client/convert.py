#! /usr/bin/python

# Converts SVG files to GCode ready for machining
# Uses the Endpoint conversion code, so should be identical

# Requires all the dependencies to be installed, including pycam
# But doesn't need the MySQL database setup or anything like that

import sys, os
sys.path.append('../www')
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'
from django.conf import settings

import tempfile
import os
import argparse

from cursivelib.robot_spec import *
from cursivelib.svg_to_gcode import *
from cursivelib.pycam_gcode import *
from cursivelib.native_gcode import *
import cursivelib.svg as svg
from cursivedata.models.endpoint import *

from cursivelib.robot_spec import add_botspec_arguments
from cursivelib.robot_spec import get_botspec_from_args



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert SVG files to GCode for drawing")

    add_botspec_arguments(parser)
    parser.add_argument('--direct',
        action='store', dest='direct', type=bool, default=True,
        help="Do the conversion directly (otherwise, make an Endpoint and use that (for testing...)")
    parser.add_argument('--native',
        action='store', dest='native', type=bool, default=False,
        help="Use the native conversion instead of PyCam")
    parser.add_argument('--width',
        action='store', dest='width', type=int, default='500',
        help="Desired drawing width")
    parser.add_argument('--input',
        action='store', dest='input', type=str, required=True,
        help="Input SVG file")
    parser.add_argument('--output',
        action='store', dest='output', type=str, required=True,
        help="Output SVG file")

    args = parser.parse_args()

    # Specifications of the robot which will do the drawing
    robot_spec = get_botspec_from_args(args)
    print "Got bot spec: ",robot_spec.show()
    sys.exit()

    # File to put gcode into
    output_gcode = args.output

    # Desired width of final drawing
    width = args.width

    #Input SVG file
    svg_file = args.input
    print "Input SVG File: ",  svg_file
    svg_data = parse(svg_file)
    direct = args.direct
    print "Args.direct: ", args.direct
    direct = True
    print "Direct: ", direct
    native = args.native
    print "Native ", native


    if direct :
        print "Direct conversion"
        preparation = SVGPreparation()
        
        # Create a drawing position this into a drawing position (x,y offsets and scale)
        drawing_position = preparation.drawing_position_from_file( svg_file, DrawingSpec(width=args.width)
    , robot_spec) 

        # Setup the transforms from drawing to page and page to robot
        print "Making SVG transforms"
        drawing_to_page = preparation.get_drawing_transform(drawing_position)
        page_to_robot = preparation.get_robot_transform(robot_spec)

        # Apply the transforms to the SVG data
        page_svg = preparation.apply_into_data(svg_data,robot_spec.svg_drawing(),drawing_to_page)
        robot_svg = preparation.apply_into_data(page_svg,robot_spec.svg_total(),page_to_robot)

        if native:
            gcode_converter = NativeGCodeConversion()
        else:
            gcode_converter = PyCAMGcode()
        print "Convert to GCode into " + output_gcode
        gcode_converter.convert_svg(robot_svg,output_gcode,robot_spec)
    else :
        print "Creating endpoint to process file"
        end_point = Endpoint(name="Local",device="Local",location="Local" ,
            width=robot_spec.width, height=robot_spec.height, 
            top_margin=robot_spec.top_margin, side_margin=robot_spec.side_margin, generate_gcode=True)
        pos = end_point.pos_from_file(svg_file,width)
        filename = end_point.draw_svg(svg_file,pos,localfile=output_gcode)

