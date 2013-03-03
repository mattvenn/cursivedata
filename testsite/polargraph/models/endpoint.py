'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
import polargraph.svg as svg
from polargraph.models.drawing_state import DrawingState,StoredOutput
import pysvg.structure
import pysvg.builders
from pysvg.parser import parse
import re
import tempfile
import subprocess
import os



'''
A robot or other output device

The robot has margins - undrawable areas which shouldn't be used in drawings. To 
deal with this:
* width is the width of the robot (i.e. the distance between the stepper motors
* side_margin/top_margin are the undrawable areas
* the robot will calculate img_width and img_height, i.e. the size of the image once
  margins are taken into account

All of the SVG files use img_width and img_height. 0,0 in an SVG file will be the top left of the
drawable area.

Transform SVG will transform input SVG into this coordinate system, according to the Pipeline's
definition of where the SVG should go.

Create GCode will take the SVG (in Page coordinates) and transform them into Robot coordinates,
i.e. translate them by side_margin and top_margin
'''
class Endpoint( DrawingState ):
    name = models.CharField(max_length=200)
    device = models.CharField(max_length=200)
    #Width of the robot - not width of the drawing, which is img_width
    width = models.FloatField(max_length=200)
    #Height of the robot - not height of the drawing, which is img_height
    height = models.FloatField(max_length=200)
    #Robot margins - the undrawable area on each side and at the top
    side_margin = models.FloatField(max_length=200)
    top_margin = models.FloatField(max_length=200)
    paused = models.BooleanField(default=False)
    #add this to db, using url for now
    status = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    robot_svg_file = models.CharField(max_length=200,blank=True)

    def __init__(self, *args, **kwargs):
        super(Endpoint, self).__init__(*args, **kwargs)
        #Set the actual size of the drawing area based on the size of the robot and the margins
        #Used to make the SVG images
        self.img_width = self.width - self.side_margin * 2
        self.img_height = self.height - self.top_margin
        #Used by the GCode parser to check sizes
        self.x_min = self.side_margin
        self.y_min = self.top_margin
        self.x_max = self.side_margin + self.img_width
        self.y_max = self.top_margin + self.img_height
   
    def input_svg(self,svg_file, pipeline ):
  #      print "Adding SVG"
#        import pdb; pdb.set_trace()
        try:
            current_drawing = self.transform_svg(svg_file,pipeline)
  #          print current_drawing.getXML()
            #this will save out the latest svg as a file
            self.add_svg(current_drawing)
        except Exception as e:
            print "Problem updating SVG in endpoint:",e
        try:
            #easy comment out gcode for speedier testing.
            if True:
                #now make the gcode
                so = GCodeOutput(endpoint=self)
                so.save()
                #transform the current svg for the robot
                current_drawing = self.transform_svg_for_robot(self.last_svg_file)

                #write it out as an svg
                self.robot_svg_file = self.get_robot_svg_filename()
                current_drawing.save(self.robot_svg_file)
                self.save()

                #convert it to gcode
                self.convert_svg_to_gcode(self.robot_svg_file,so.get_filename())
        except Exception as e:
            print "Coudldn't make GCode:",e
            so.delete()

    #could do clipping? http://code.google.com/p/pysvg/source/browse/trunk/pySVG/src/tests/testClipPath.py?r=23
    #returns an svg document (not a file)
    def transform_svg_for_robot(self, svg_file): 
        current_drawing = self.create_svg_doc(self.width,self.height)
        try:
            svg_data = parse(svg_file)

            #setup our transform
            tr = pysvg.builders.TransformBuilder()
            tr.setScaling(x=1,y=-1)
            trans = str(self.side_margin) + " " + str(self.img_height) 
            tr.setTranslation( trans )
#            print "Endpoint transform:"+tr.getTransform()
            group = pysvg.structure.g()
            group.set_transform(tr.getTransform())
            #add the drawing
            for element in svg_data.getAllElements():
                group.addElement(element)

            current_drawing.addElement(group)
            return current_drawing
        except Exception as e:
            print "Couldn't transform SVG for robot:",svg_file,e        

    #returns an svg document (not a file)
    def transform_svg(self, svg_file, pipeline): 
        current_drawing = self.create_svg_doc()
        try:
            xoffset = pipeline.print_top_left_x
            yoffset = pipeline.print_top_left_y
            scale = pipeline.print_width / pipeline.img_width
            svg_data = parse(svg_file)

            #set up pipeline's transform
            tr = pysvg.builders.TransformBuilder()
            tr.setScaling(scale)
            trans = str(xoffset) + " " + str(yoffset) 
            tr.setTranslation( trans )
#            print "Pipeline transform:"+tr.getTransform()
            group = pysvg.structure.g()
            group.set_transform(tr.getTransform())

            for element in svg_data.getAllElements():
                group.addElement(element)

            current_drawing.addElement(group)
            return current_drawing
        except Exception as e:
            print "Couldn't transform SVG for pipeline:",svg_file,e        

    #use pycam and parse_gcode to turn svg into robot style files
    def convert_svg_to_gcode(self, svgfile, polarfile ):
        fd, tmp_gcode = tempfile.mkstemp()
        pycam="/usr/bin/pycam"
        pycam_args = [pycam, svgfile, "--export-gcode=" + tmp_gcode, "--process-path-strategy=engrave"]
        #print pycam_args
        p = subprocess.Popen( pycam_args, stdout=subprocess.PIPE,stderr=subprocess.PIPE )
        stdout,stderr = p.communicate()
        self.parse_gcode_to_polar(tmp_gcode,polarfile)
        os.close(fd)
        os.remove(tmp_gcode)

    #this goes through a gcode file (*.ngc) and chucks out all comments and commands we don't use
    #the output is validated to ensure it won't command the robot to move outside its drawing area
    #then the output is saved to a polar file ready to be served
    def parse_gcode_to_polar(self,infile,outfile):
        try:
            gcode = open(infile)
        except:
            print "bad file"
            exit( 1 )

        gcodes = gcode.readlines()
        gcode.close()

        startCode = re.compile( "^G([01])(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
        contCode =  re.compile( "^(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
        lastX = None
        lastY = None
        polar_code=""
        for line in gcodes:
            s = startCode.match(line)
            c = contCode.match(line)
            gcode = 0
            if s:
                gcode = s.group(1)
                x = s.group(2)
                y = s.group(3)
                z = float(s.group(4))
                if z > 0 :
                    #don't draw
                    polar_code += "d0\n"
                else:
                    #draw
                    polar_code += "d1\n"
            elif c: 
                try:
                    x = float(c.group(1))
                except:
                    x = lastX 
                try:
                    y = float(c.group(2))
                except:
                    y = lastY

                outx = x
                outy = y 

                #validate, the +-1mm is to account for rounding errors
                if outx > self.x_max + 1:
                    raise Exception("gcode x too large %f > %f" % (outx,self.x_max))
                if outy > self.y_max + 1:
                    raise Exception("gcode y too large %f > %f" % (outy,self.y_max))
                if outx < self.x_min - 1:
                    raise Exception("gcode x too small %f < %f" % (outx,self.x_min))
                if outy < self.y_min - 1:
                    raise Exception("gcode y too small %f < %f" % (outy,self.y_min))

                polar_code += "g%.1f,%.1f\n" %  (outx,outy) 
                lastX = x
                lastY = y

        file = open(outfile,"w")
        #print "writing polar file to ", outfile
        file.write(polar_code)
                
    def get_next_filename(self):
        n = self.get_next()
        if n:
            return n.get_filename()
        return None
    
    def get_num_files_to_serve(self):
        try:
            return len(GCodeOutput.objects.filter(endpoint=self,served=False))
        except Exception as e:
            return None

    def mark_all_gcode_served(self):
        for gcode in GCodeOutput.objects.filter(endpoint=self,served=False):
            gcode.served = True
            gcode.save()

    def get_next(self):
        try:
            return GCodeOutput.objects.filter(endpoint=self,served=False).order_by('modified')[:1].get()
        except Exception as e:
            return None
        
    def consume(self):
        n = self.get_next()
        n.served = True
        n.save()

    def resume(self):
        self.paused = False
        self.save()

    def pause(self):
        self.paused = True
        self.save()
    
    def reset(self):
        super(Endpoint, self).reset()
        for gcode in GCodeOutput.objects.filter(endpoint=self,served=False):
            gcode.delete()
        
    def get_stored_output(self,output_type,status):
        try:
            return StoredOutput.objects.get(endpoint=self,pipeline=None,generator=None,run_id=self.run_id,filetype=output_type,status=status)
        except:
            return StoredOutput(endpoint=self,pipeline=None,generator=None,run_id=self.run_id,filetype=output_type,status=status)
    
    def get_recent_output(self,start=0,end=8):
        return StoredOutput.objects.order_by('-modified') \
                .filter(endpoint=self,pipeline=None,status="complete",filetype="svg")\
                .exclude(run_id= self.run_id)[start:end]
      
    def get_robot_svg_filename(self):
        return self.get_filename("robot", "svg")

    def get_output_name(self):
        return "endpoint"
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'polargraph'

class GCodeOutput( models.Model ):
    endpoint = models.ForeignKey(Endpoint)
    served = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)
    
    def get_filename(self):
        if not self.id > 0:
            self.save()
        return "data/output/gcode/"+str(self.id)+".gcode"
    
    def delete(self):
        try:
            os.remove(self.get_filename())
        except Exception as e:
            print "Couldn't remove GCode file",self.get_filename,e
        super(GCodeOutput, self).delete()
    
    class Meta:
        app_label = 'polargraph'
