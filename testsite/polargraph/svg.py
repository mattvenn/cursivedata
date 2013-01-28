'''
Created on 6 Jan 2013

@author: dmrust
'''
import time
from pysvg.parser import parse
import polargraph.parse_gcode
import sys
import subprocess
import cairosvg


#Append one svg file to another svg file
#NOTE: currently just copies one file to the other
def append_svg_to_file( fragment_file, main_file ):
    try :
        svg_main = parse(main_file)
        svg_frag = parse(fragment_file)
        for e in svg_frag.getAllElements():
            svg_main.addElement( e )
        svg_main.save(main_file)
    except Exception as e:
        print "Coudlnt' read input file:",fragment_file,e

#use pycam and parse_gcode to turn svg into robot style files
def convert_svg_to_gcode( endpoint,generator_params,svgfile, polarfile ):
    try :
        gcodefile="/tmp/tmp.gcode" #should be unique for process
        pycam="/home/polarsite/pycam-0.5.1/pycam"
        pycam_args = [pycam, svgfile, "--export-gcode=" + gcodefile, "--process-path-strategy=engrave"]
        result = subprocess.call(pycam_args)
        polargraph.parse_gcode.parse(endpoint,generator_params,gcodefile,polarfile)
    except Exception as e:
        print "Coudlnt' read input SVG file to make GCODE:",svgfile,e


def convert_svg_to_png( svgfile, pngfilename ):
    with open( pngfilename, 'w+') as png_file:
        print "Writing PNG file:",pngfilename," from ",svgfile," got",str(png_file)
        cairosvg.svg2png(url=svgfile,write_to=png_file)

def get_temp_filename(extension):
    millis = int(round(time.time() * 1000000))
    return "tmp/tmpfile"+str(millis)+"."+extension

def write_temp_svg_file( svgstring ):
    fn = get_temp_filename("svg")
    with open( fn, "wb" ) as outfile:
        outfile.write( svgstring)
    
    return fn
