'''
Created on 6 Jan 2013

@author: dmrust
'''
import time,copy
from pysvg.parser import parse
import sys
import cairosvg
from xml.parsers.expat import ExpatError


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
def append_svg_to_file( fragment_file, main_file ):

    #locking
    import fcntl

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
        svg_main = parse(main_file)
        print "parsing frag file", fragment_file
        svg_frag = parse(fragment_file)
        svg_id = int(time.time())
        for e in svg_frag.getAllElements():
            try:
                e.set_id(svg_id)
                e.set_class("frame")
            except AttributeError:
                pass
            svg_main.addElement( e )
        svg_main.save(main_file)
    except (ExpatError, IOError) as e:
        print "problem appending %s to %s: %s" % (fragment_file,main_file,e)
        raise
    clear_blank_lines(main_file)

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
