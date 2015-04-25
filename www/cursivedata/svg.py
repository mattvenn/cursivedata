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
    with open( pngfilename, 'w+') as png_file:
        log.debug("NOT converting SVG %s to PNG" % (svgfile))
        #cairosvg.svg2png(url=svgfile,write_to=png_file)
        log.debug("done")

def get_temp_filename(extension):
    millis = int(round(time.time() * 1000000))
    return "tmp/tmpfile"+str(millis)+"."+extension

def write_temp_svg_file( svgstring ):
    fn = get_temp_filename("svg")
    with open( fn, "wb" ) as outfile:
        outfile.write( svgstring)
    
    return fn
