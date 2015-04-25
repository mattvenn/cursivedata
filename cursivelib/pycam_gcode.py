import tempfile
import subprocess
import os
import re

import logging
log = logging.getLogger('pycam_conversion')

# a fantastic error class!
class PyCAMConversionError(Exception):
    pass

class PyCAMGcode() :
    pycam="/usr/bin/pycam"
    #pycam="/Users/dmrust/.virtualenvs/polarsite/lib/python2.7/site-packages/pycam-0.5.1/pycam"
    
    def convert_svg(self,svg_data,gcode_filename,robot_spec) :
        fd, tmp_gcode = tempfile.mkstemp()
        svg_fg, tmp_svg = tempfile.mkstemp(".svg")
        log.debug("Saving SVG as %s" % tmp_svg)
        svg_data.save(tmp_svg)
        pycam_args = [self.pycam, tmp_svg, "--export-gcode=" + tmp_gcode, "--process-path-strategy=engrave"]
        log.debug("pycam args %s" % pycam_args)

        p = subprocess.Popen( pycam_args, stdout=subprocess.PIPE,stderr=subprocess.PIPE )
        stdout,stderr = p.communicate()
        log.debug("pycam done")

        self.parse_gcode_to_polar(tmp_gcode,gcode_filename,robot_spec)
        os.close(fd)
        os.remove(tmp_gcode)
        os.remove(tmp_svg)

        #this goes through a gcode file (*.ngc) and chucks out all comments and commands we don't use
    #the output is validated to ensure it won't command the robot to move outside its drawing area
    #then the output is saved to a polar file ready to be served
    def parse_gcode_to_polar(self,infile,outfile,robot_spec=None):
        gcode = open(infile)

        gcodes = gcode.readlines()
        gcode.close()

        startCode = re.compile( "^G([01])(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
        contCode =  re.compile( "^(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
        lastX = None
        lastY = None
        polar_code=[]
        ns = 0
        nc = 0
        nd = 0
        for line in gcodes:
            s = startCode.match(line)
            c = contCode.match(line)
            gcode = 0
            if s:
                ns += 1
                gcode = s.group(1)
                x = s.group(2)
                y = s.group(3)
                z = float(s.group(4))
                if z > 0 :
                    #don't draw, but ensure previous gcode also wasn't d0
                    if len(polar_code) and polar_code[-1] != 'd0':
                        polar_code.append("d0")
                else:
                    #draw
                    polar_code.append("d1")
            elif c: 
                nc += 1
                x = float(c.group(1) or lastX)
                y = float(c.group(2) or lastY)

                outx = x
                outy = y 

                #validate, the +-1mm is to account for rounding errors
                if robot_spec is not None:
                    if outx > robot_spec.x_max:
                        raise PyCAMConversionError("gcode x too large %f > %f" % (outx,self.x_max))
                    if outy > robot_spec.y_max:
                        raise PyCAMConversionError("gcode y too large %f > %f" % (outy,self.y_max))
                    if outx < robot_spec.x_min:
                        raise PyCAMConversionError("gcode x too small %f < %f" % (outx,self.x_min))
                    if outy < robot_spec.y_min:
                        raise PyCAMConversionError("gcode y too small %f < %f" % (outy,self.y_min))

                polar_code.append("g%.1f,%.1f" %  (outx,outy))
                lastX = x
                lastY = y
            else: 
                nd += 1

        file = open(outfile,"w")
        log.debug("writing polar file to %s" % outfile)
        log.debug("Discarded: %s Start: %s, Continue: %s" % ( nd,ns,nc))
        for line in polar_code:
            file.write(line + "\n")
        file.close()

