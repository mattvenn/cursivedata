import tempfile
import subprocess
import os
import re
import ipdb

MIN_LENGTH = 1.0
#requires version 2.0b1
from svgpath import Path, Line, Arc, CubicBezier, QuadraticBezier, parse_path

# a fantastic error class!
class GCodeConversionError(Exception):
    pass

        

class Transform() :
    def __init__(self,xoffset=0,yoffset=0,xscale=1,yscale=1,parent=None):
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.xscale = xscale
        self.yscale = yscale
        self.parent = parent

    def transform(self,x,y) :
        #do our transform first
        xt = x*self.xscale + self.xoffset
        yt = y*self.yscale + self.yoffset
        #then parents
        if self.parent is not None:
            xt,yt = self.parent.transform(xt,yt)
        return (xt,yt)

    # e.g. translate(110 0) scale(1.07513227513 1.07513227513)
    def set_from_string(self,input):
        print "Using Input: ",input
        print "Type: ",input.__class__.__name__
        tr = re.compile(".*translate\(([^, ]+)[, ]+([^, ]+)\).*")
        scale = re.compile(".*scale\(([^, ]+)[, ]+([^, ]+)\).*")
        trm = tr.match(str(input))
        scm = scale.match(str(input))
        if trm:
            print "Got translate: ", trm.group(1),trm.group(2)
            self.xoffset = float(trm.group(1))
            self.yoffset = float(trm.group(2))
        if scm:
            print "Got scale: ", scm.group(1),scm.group(2)
            self.xscale = float(scm.group(1))
            self.yscale = float(scm.group(2))


class NativeGCodeConversion() :
    outfile = None
    
    def convert_svg(self,svg_data,gcode_filename,robot_spec) :
        self.outfile = open(gcode_filename,'w')
        self.convert_elements(svg_data)
        self.outfile.close()
        

    def convert_elements(self,svg_data,transform=Transform()):
        
        for element in svg_data.getAllElements():
            n = element.__class__.__name__
#            ipdb.set_trace()
            if n is 'g':
                # It's a group, so process all the stuff in it
                tr = element.get_transform()
                trans = Transform(parent=transform)
                trans.set_from_string(tr)
                self.convert_elements(element,trans)
            elif n is 'path':
                self.convert_path(element,transform)
            else:
                print "Unknown element: ",n


    def convert_path(self,path,transform) :
        segments = parse_path(path.get_d())
        last = complex(float("inf"),float("inf"))
        # Also assumes that starts and ends are contiguous
        for seg in segments:
            start = seg.start

            # In case segments are non-contiguous
            if abs(start-last) > 0.001:
                self.pen_up()
                self.output_move(start.real,start.imag,transform)
                self.pen_down()

            #point method interpolates x,y from start to end as 0 >= i <= 1
            #this loop may cause a problem with not properly closed shapes
            if not type(seg) is Line:
                length = seg.length(error=0.01)
                inc = MIN_LENGTH/length
                i = 0
                while i <= 1:
                    i += inc
                    p = seg.point(i)
                    self.output_move(p.real,p.imag,transform)

            last = seg.end
            self.output_move(last.real,last.imag,transform)
        self.pen_up()

    def output_move(self,x,y,transform):
        xt,yt = transform.transform(x,y)
#        print "Translated",x,y,"to",xt,yt
        self.output("g"+format(xt,".1f")+","+format(yt,".1f"))

    def pen_up(self):
        self.output("d0")

    def pen_down(self):
        self.output("d1")

    def output(self, data) :
#        print "OP: ", data
        self.outfile.write(data+"\n")

