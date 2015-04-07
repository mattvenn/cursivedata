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
from django.utils import timezone

import logging
log = logging.getLogger('graphics')

def get_dimensions(svg_file):
    parsed = parse(svg_file)
    #rewind to avoid an error when the file is parsed again
    svg_file.seek(0)
    #this is wrong #FIXME
    #might be 0
    width = parsed.getAttribute('width')
    height = parsed.getAttribute('height')

    #try viewbox
    if width == None or height == None:
        viewbox = parsed.get_viewBox()
        width = viewbox.split(' ')[2]
        height = viewbox.split(' ')[3]
    
    if width == None or height == None:
        #abort!
        raise Exception("couldn't get width or height of uploaded svg")
    pixtomm = 3.55
    #FIXME bad way of handling svg sizes
    if width.endswith("px"):
        width = float(width.rstrip("px"))
    else:
        width = float(width)

    if height.endswith("px"):
        height = float(height.rstrip("px"))
    else:
        height = float(height)

    return (width,height)

#Append one svg file to another svg file
#NOTE: currently just copies one file to the other
def append_svg_to_file(fragment_file, main_file):
    #locking
    import fcntl
    start_time = time.time()

    try:
        lockfile = "/tmp/%s.lock" % main_file.replace('/','.')
        fd = open(lockfile,'w')

        log.debug("checking lock: %s" % lockfile)
        fcntl.lockf(fd,fcntl.LOCK_EX | fcntl.LOCK_NB)
        log.debug("ok")
    except IOError, e:
        log.warning("lock in use: %s" % lockfile)
        raise

    try:
        log.debug("parsing main file %s" % main_file)
        svg_main = ET.parse(main_file)
        log.debug("parsing frag file %s" % fragment_file)
        svg_frag = ET.parse(fragment_file)
        svg_id = str(int(time.time()))
        log.debug("using svg_id as %s" % svg_id)
        mainroot= svg_main.getroot()
        fragroot =svg_frag.getroot()
        log.debug("adding frags to main %s" % main_file)
        for child in fragroot:
            child.set('id',svg_id)
            child.set('class','frame')
            mainroot.append(child)
            
        svg_main.write(main_file)
    except ParseError as e:
        log.exception("problem appending %s to %s" % (fragment_file,main_file))
        raise
    #no need to do this with new parser
    #clear_blank_lines(main_file)
    log.info("finished in %d secs" % (time.time() - start_time))

def is_blank_line(line):
    if line == "\n":
        return True
    return False

def clear_blank_lines(main_file):
    log.debug("cleaning blank lines from %s" % main_file)
    f = open(main_file)
    lines = f.readlines()
    f.close()
    noblanks = [ x for x in lines if x != '\n' ]
    f = open(main_file,'w')
    f.writelines(noblanks)
    f.close()


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
