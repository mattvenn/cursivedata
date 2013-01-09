'''
Created on 6 Jan 2013

@author: dmrust
'''
import time


#Append one svg file to another svg file
#NOTE: currently just copies one file to the other
def append_svg_to_file( fragment_file, main_file ):
    try :
        with open( fragment_file, "rb") as infile:
            try :
                with open( main_file, "a+") as outfile :
                    for line in infile :
                        outfile.write( line )
            except Exception as ex:
                print "Coudlnt' create outputfile:",main_file,ex
    except Exception as e:
        print "Coudlnt' read input file:",fragment_file,e

#Append an svg string to an svg file
#NOTE: currently just copies one file to the other
def convert_svg_to_gcode( svgfile, gcodefile ):
    try :
        with open( svgfile, 'rb' ) as source:
            try :
                with open( gcodefile, 'a+' ) as dest:
                    for line in source :
                        line=line.replace("SVG","GCODE")
                        dest.write( line )
            except Exception as ex:
                print "Coudlnt' create outputfile:",svgfile,ex
    except Exception as e:
        print "Coudlnt' read input file:",svgfile,e

def get_temp_filename(extension):
    millis = int(round(time.time() * 1000))
    return "tmp/tmpfile"+str(millis)+"."+extension

def write_temp_svg_file( svgstring ):
    fn = get_temp_filename("svg")
    with open( fn, "wb" ) as outfile:
        outfile.write( svgstring)
    return fn