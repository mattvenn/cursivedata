import time,copy
from pysvg.parser import parse
import pysvg.structure
import pysvg.builders

import time
import sys
from xml.parsers.expat import ExpatError
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


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
    if width.endswith("mm"):
        width = float(width.rstrip("mm"))
    else:
        width = float(width)

    if height.endswith("px"):
        height = float(height.rstrip("px"))
    if height.endswith("mm"):
        height = float(height.rstrip("mm"))
    else:
        height = float(height)

    return (width,height)

#Append one svg file to another svg file
#NOTE: currently just copies one file to the other
def append_svg_to_file( fragment_file, main_file ):

    #locking
    import fcntl
    start_time = time.time()

    try:
        lockfile = "/tmp/%s.lock" % main_file.replace('/','.')
        fd = open(lockfile,'w')

        print "checking lock:", lockfile
        fcntl.lockf(fd,fcntl.LOCK_EX | fcntl.LOCK_NB)
        print "ok"
    except IOError, e:
        print "lock in use:", lockfile
        raise

    try:
        print "parsing main file", main_file
        svg_main = ET.parse(main_file)
        print "parsing frag file", fragment_file
        svg_frag = ET.parse(fragment_file)
        svg_id = str(int(time.time()))
        mainroot= svg_main.getroot()
        fragroot =svg_frag.getroot()
        print "adding frags to main", main_file
        for child in fragroot:
            child.set('id',svg_id)
            child.set('class','frame')
            mainroot.append(child)
            
        svg_main.write(main_file)
    except ParseError as e:
        print "problem appending %s to %s: %s" % (fragment_file,main_file,e)
        raise
    #no need to do this with new parser
    #clear_blank_lines(main_file)
    print "finished in %d secs" % (time.time() - start_time)

def is_blank_line(line):
    if line == "\n":
        return True
    return False

def clear_blank_lines(main_file):
    print "cleaning blank lines from ", main_file
    f = open(main_file)
    lines = f.readlines()
    f.close()
    noblanks = [ x for x in lines if x != '\n' ]
    f = open(main_file,'w')
    f.writelines(noblanks)
    f.close()

#Create an empty svg doc with the given width and height (mm)
def create_svg_doc(width,height,createRect=False):
    widthmm = "%fmm" % width
    heightmm = "%fmm" % height
    doc = pysvg.structure.svg(width=widthmm,height=heightmm)
    doc.set_viewBox("0 0 %s %s" % (width, height))
    if createRect:
        build = pysvg.builders.ShapeBuilder()
        doc.addElement(build.createRect(0, 0, width="100%", height="100%", fill = "rgb(255, 255, 255)"))
    return doc

