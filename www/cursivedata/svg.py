'''
Created on 6 Jan 2013

@author: dmrust
'''
import time,copy
from pysvg.parser import parse
import time
import sys
import cairosvg
from xml.parsers.expat import ExpatError
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


def convert_svg_to_png( svgfile, pngfilename ):
    exit(1)
    with open( pngfilename, 'w+') as png_file:
        #print "Writing PNG file:",pngfilename," from ",svgfile," got",str(png_file)
        cairosvg.svg2png(url=svgfile,write_to=png_file)

def get_temp_filename(extension):
    exit(1)
    millis = int(round(time.time() * 1000000))
    return "tmp/tmpfile"+str(millis)+"."+extension

def write_temp_svg_file( svgstring ):
    exit(1)
    fn = get_temp_filename("svg")
    with open( fn, "wb" ) as outfile:
        outfile.write( svgstring)
    
    return fn
