'''
Created on 6 Jan 2013

@author: dmrust
'''
filenum = 1

#Append one svg file to another svg file
#NOTE: currently just copies one file to the other
def append_svg_to_file( fragment_file, main_file ):
    with open( fragment_file, "rb") as infile:
        with open( main_file, "wb") as outfile :
            for line in infile :
                outfile.write( line )

#Append an svg string to an svg file
#NOTE: currently just copies one file to the other
def convert_svg_to_gcode( svgfile, gcodefile ):
    with open( svgfile, 'rb' ) as source:
        with open( gcodefile, 'wb' ) as dest:
            for line in source :
                dest.write( line )

def get_temp_filename(extension):
    filenum += 1
    return "tmp/tmpfile"+filenum+"."+extension

def write_temp_svg_file( svgstring ):
    fn = get_temp_filename("svg")
    with open( fn, "wb" ) as outfile:
        outfile.write( svgstring)
    return fn