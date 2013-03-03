'''
Created on 6 Jan 2013

@author: dmrust
'''
import time
from pysvg.parser import parse
import sys
import cairosvg


#Append one svg file to another svg file
#NOTE: currently just copies one file to the other
def append_svg_to_file( fragment_file, main_file ):
    try:
        svg_main = parse(main_file)
        svg_frag = parse(fragment_file)
        for e in svg_frag.getAllElements():
            svg_main.addElement( e )
        svg_main.save(main_file)
    except Exception as e:
        print "couldn't add %s to %s: %s" % (fragment_file,main_file,e)


def convert_svg_to_png( svgfile, pngfilename ):
    with open( pngfilename, 'w+') as png_file:
        #print "Writing PNG file:",pngfilename," from ",svgfile," got",str(png_file)
        cairosvg.svg2png(url=svgfile,write_to=png_file)

def get_temp_filename(extension):
    millis = int(round(time.time() * 1000000))
    return "tmp/tmpfile"+str(millis)+"."+extension

def write_temp_svg_file( svgstring ):
    fn = get_temp_filename("svg")
    with open( fn, "wb" ) as outfile:
        outfile.write( svgstring)
    
    return fn
