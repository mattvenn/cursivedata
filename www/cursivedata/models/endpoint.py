'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
from django.utils import timezone
import cursivedata.svg as svg
from cursivedata.models.drawing_state import DrawingState,StoredOutput
import pysvg.structure
import pysvg.builders
from pysvg.parser import parse
import re
import tempfile
import subprocess
import os


# a fantastic error class!
class EndpointConversionError(Exception):
    pass


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
    name = models.CharField(max_length=200,default="default")
    generate_gcode = models.BooleanField(default=False)
    device = models.CharField(max_length=200,default="web")
    #Width of the robot - not width of the drawing, which is img_width
    width = models.FloatField(max_length=200,default=200)
    #Height of the robot - not height of the drawing, which is img_height
    height = models.FloatField(max_length=200,default=200)
    #Robot margins - the undrawable area on each side and at the top
    side_margin = models.FloatField(max_length=200,default=10)
    top_margin = models.FloatField(max_length=200,default=10)
    paused = models.BooleanField(default=False)
    #add this to db, using url for now
    status = models.CharField(max_length=200,default="default")
    location = models.CharField(max_length=200,default="default")
    robot_svg_file = models.CharField(max_length=200,blank=True)
    #when the status was last updated
    status_updated = models.DateTimeField("Last Updated",blank=True,null=True)

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
 
    #returns true if updated within last hour
    @property
    def is_live(self):
        live_date = timezone.now()-timezone.timedelta(hours=1)
        if self.status_updated > live_date:
            return True
        return False
       
    def load_external_svg(self,svg_file,width):
        transform = Transform()
        transform.build_from_endpoint(self,svg_file,width)
        self._input_svg(svg_file,transform)

    def input_svg(self,svg_file, pipeline ):
        transform = Transform()
        transform.build_from_pipeline(pipeline)
        self._input_svg(svg_file,transform)

    #how to name this?
    def _input_svg(self,svg_file,transform):
        current_drawing = self.transform_svg(svg_file,transform)

        #this will save out the latest svg as a file
        self.add_svg(current_drawing)

        #transform the current svg for the robot
        current_drawing = self.transform_svg_for_robot(self.last_svg_file)

        #write it out as an svg
        self.robot_svg_file = self.get_robot_svg_filename()
        current_drawing.save(self.robot_svg_file)
        self.save()

        #convert it to gcode
        if self.generate_gcode:
            try:
                so = GCodeOutput(endpoint=self)
                so.save()
                print "creating gcode in %s from %s" % (so.get_filename(), self.robot_svg_file)
                self.convert_svg_to_gcode(self.robot_svg_file,so.get_filename())
            except EndpointConversionError, e:
                print "problem converting svg:", e
                so.delete()
                raise EndpointConversionError(e)

    #could do clipping? http://code.google.com/p/pysvg/source/browse/trunk/pySVG/src/tests/testClipPath.py?r=23
    #returns an svg document (not a file)
    def transform_svg_for_robot(self, svg_file): 
        current_drawing = self.create_svg_doc(self.width,self.height)
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

    #returns an svg document (not a file)
    def transform_svg(self, svg_file, transform): 
        current_drawing = self.create_svg_doc()
        xoffset = transform.xoffset
        yoffset = transform.yoffset
        scale = transform.scale
        svg_data = parse(svg_file)

        #set up transform
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

    #use pycam and parse_gcode to turn svg into robot style files
    def convert_svg_to_gcode(self, svgfile, polarfile ):
        fd, tmp_gcode = tempfile.mkstemp()
        pycam="/usr/bin/pycam"
        #pycam="/Users/dmrust/.virtualenvs/polarsite/lib/python2.7/site-packages/pycam-0.5.1/pycam"
        pycam_args = [pycam, svgfile, "--export-gcode=" + tmp_gcode, "--process-path-strategy=engrave"]
        print pycam_args
        p = subprocess.Popen( pycam_args, stdout=subprocess.PIPE,stderr=subprocess.PIPE )
        stdout,stderr = p.communicate()

        self.parse_gcode_to_polar(tmp_gcode,polarfile)
        os.close(fd)
        os.remove(tmp_gcode)

    #this goes through a gcode file (*.ngc) and chucks out all comments and commands we don't use
    #the output is validated to ensure it won't command the robot to move outside its drawing area
    #then the output is saved to a polar file ready to be served
    def parse_gcode_to_polar(self,infile,outfile):
        gcode = open(infile)

        gcodes = gcode.readlines()
        gcode.close()

        startCode = re.compile( "^G([01])(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
        contCode =  re.compile( "^(?: X(\S+))?(?: Y(\S+))?(?: Z(\S+))?$")
        lastX = None
        lastY = None
        polar_code=[]
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
                    #don't draw, but ensure previous gcode also wasn't d0
                    if len(polar_code) and polar_code[-1] != 'd0':
                        polar_code.append("d0")
                else:
                    #draw
                    polar_code.append("d1")
            elif c: 
                x = float(c.group(1) or lastX)
                y = float(c.group(2) or lastY)

                outx = x
                outy = y 

                #validate, the +-1mm is to account for rounding errors
                if outx > self.x_max:
                    raise EndpointConversionError("gcode x too large %f > %f" % (outx,self.x_max))
                if outy > self.y_max:
                    raise EndpointConversionError("gcode y too large %f > %f" % (outy,self.y_max))
                if outx < self.x_min:
                    raise EndpointConversionError("gcode x too small %f < %f" % (outx,self.x_min))
                if outy < self.y_min:
                    raise EndpointConversionError("gcode y too small %f < %f" % (outy,self.y_min))

                polar_code.append("g%.1f,%.1f" %  (outx,outy))
                lastX = x
                lastY = y

        file = open(outfile,"w")
        #print "writing polar file to ", outfile
        for line in polar_code:
            file.write(line + "\n")
        file.close()
                
    def get_next_filename(self):
        n = self.get_next()
        if n:
            return n.get_filename()
        return None
    
    def get_num_files_to_serve(self):
        return GCodeOutput.objects.filter(endpoint=self,served=False).count()

    def mark_all_gcode_served(self):
        for gcode in GCodeOutput.objects.filter(endpoint=self,served=False):
            gcode.served = True
            gcode.save()

    def get_next(self):
        try:
            return GCodeOutput.objects.filter(endpoint=self,served=False).order_by('modified')[:1].get()
        except GCodeOutput.DoesNotExist:
            return None
        
    def consume(self):
        n = self.get_next()
        n.served = True
        n.save()
    
    def movearea(self):
        so = GCodeOutput(endpoint=self)
        so.save()
        f = open(so.get_filename(),'w')
        f.write("g%.1f,%.1f\n" % ( self.side_margin, self.top_margin ))
        f.write("g%.1f,%.1f\n" % ( self.width - self.side_margin , self.top_margin ))
        f.write("g%.1f,%.1f\n" % ( self.width - self.side_margin , self.height ))
        f.write("g%.1f,%.1f\n" % ( self.side_margin , self.height ))
        f.write("g%.1f,%.1f\n" % ( self.side_margin, self.top_margin ))
        f.close()

    def calibrate(self):
        so = GCodeOutput(endpoint=self)
        so.save()
        print "creating gcode in ", so.get_filename()
        f = open(so.get_filename(),'w')
        f.write("c\n")
        f.close()
         
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
        except StoredOutput.DoesNotExist:
            # XXX: The new object isn't saved. Is this intentional?
            return StoredOutput(endpoint=self,pipeline=None,generator=None,run_id=self.run_id,filetype=output_type,status=status)
    
    def get_recent_output(self,start=0,end=2):
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
        app_label = 'cursivedata'

class Transform( models.Model ):
    def build_from_pipeline(self,pipeline):
        self.xoffset = pipeline.print_top_left_x
        self.yoffset = pipeline.print_top_left_y
        self.scale = pipeline.print_width / pipeline.img_width

    def build_from_endpoint(self,endpoint,svg_file,width):
        (svgwidth,svgheight) = svg.get_dimensions(svg_file)
        if width > endpoint.img_width:
            print "not scaling larger than endpoint"
            raise EndpointConversionError("width %d is too large for endpoint, max width is %d" % (width, endpoint.img_width))
        if width == 0:
            print "not using a 0 width"
            width = endpoint.img_width
        #put it in the middle of the page
        self.xoffset = (endpoint.img_width - width ) / 2
        self.yoffset = 0
        self.scale = width / svgwidth

        print "width of svg", svgwidth
        print "desired width", width
        print "scale", self.scale
        #FIXME scale results in a pic too big. 
        #self.scale *= 0.90

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
        except OSError:
            pass
        super(GCodeOutput, self).delete()
    
    class Meta:
        app_label = 'cursivedata'
