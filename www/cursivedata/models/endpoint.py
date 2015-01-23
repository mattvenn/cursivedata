'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
from django.utils import timezone
import cursivelib.svg as svg
from cursivedata.models.drawing_state import DrawingState,StoredOutput
import pysvg.structure
import pysvg.builders
from pysvg.parser import parse
import re
import tempfile
import subprocess
import os
from cursivelib.robot_spec import RobotSpec
from cursivelib.svg_to_gcode import SVGPreparation,DrawingSpec,DrawingPosition
from cursivelib.pycam_gcode import PyCAMGcode



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
    preparation = SVGPreparation()

    def __init__(self, *args, **kwargs):
        super(Endpoint, self).__init__(*args, **kwargs)
        #Set the actual size of the drawing area based on the size of the robot and the margins
        #Used to make the SVG images
        self.robot_spec = RobotSpec(width=self.width,height=self.height,top_margin = self.top_margin, side_margin = self.side_margin)
 
    #returns true if updated within last hour
    @property
    def is_live(self):
        live_date = timezone.now()-timezone.timedelta(hours=1)
        if self.status_updated > live_date:
            return True
        return False
       
    # Called to plonk an SVG file onto the robot with the given width
    def load_external_svg(self,svg_filename,width):
        self.draw_svg(svg_filename, self.pos_from_file(svg_filename,width))

    # Called by a pipeline to add the next bit of SVG
    def input_svg(self,svg_filename, pipeline ):
        self.draw_svg(svg_filename, self.pos_from_pipeline(pipeline))



    # "Draws" an SVG file by creating GCode which is then available
    # for the robot to consume
    # Returns the gcode filename
    # Local can be set to not save intermediate files or databases
    def draw_svg(self,svg_filename,drawing_position,localfile=None):
        svg_data = parse(svg_filename)

        # Transform the SVG to match the drawing position
        page_svg = self.get_page_svg(svg_data,drawing_position)

        #this will save out the latest svg as a file
        if localfile is None:
            self.add_svg(page_svg)

        # transform the current svg for the robot coordinates
        robot_svg = self.transform_svg_for_robot(page_svg)

        #write it out as an svg
        self.robot_svg_file = self.get_robot_svg_filename()
        robot_svg.save(self.robot_svg_file)
        if localfile is None:
            self.save()

        #convert it to gcode
        if self.generate_gcode:
            try:
                if localfile is None:
                    so = GCodeOutput(endpoint=self)
                    so.save()
                    output_filename = so.get_filename()
                else:
                    output_filename = localfile

                print "creating gcode in %s from %s" % (output_filename, self.robot_svg_file)
                gcode_converter = PyCAMGcode()
                gcode_converter.convert_svg(robot_svg,output_filename,self.robot_spec)
            except EndpointConversionError, e:
                print "problem converting svg:", e
                so.delete()
                raise EndpointConversionError(e)
            print "gcode done"

    def transform_svg_for_robot(self, svg_data): 
        current_drawing = self.svg_complete()
        #setup our transform
        tr = self.preparation.get_robot_transform(self.robot_spec)
        self.preparation.apply_into_data(svg_data,current_drawing,tr)
        return current_drawing

    #returns an svg document (not a file)
    def get_page_svg(self, svg_data, drawing_position): 
        current_drawing = self.svg_drawing()
        tr = self.preparation.get_drawing_transform(drawing_position)
        self.preparation.apply_into_data(svg_data,current_drawing,tr)
        return current_drawing

    # Creates a DrawingPosition from the pipeline, according to its print area
    def pos_from_pipeline(self,pipeline) :
        return DrawingPosition(
            pipeline.print_top_left_x,
            pipeline.print_top_left_y,
            pipeline.print_width / pipeline.img_width)

    # Centers the given file in the print area
    def pos_from_file(self,svg_filename,width):
        return self.preparation.drawing_position_from_file(svg_filename,
            DrawingSpec(width=width),self.robot_spec)


    # Creates an SVG in drawing coordinates
    def svg_drawing(self) :
        return self.create_svg_doc()

    # Creates an SVG the size of the final page
    def svg_complete(self) :
        return self.create_svg_doc(self.width,self.height)

                
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
        self.robot_spec.write_outline_gcode(so.get_filename() )

    def calibrate(self):
        so = GCodeOutput(endpoint=self)
        so.save()
        print "creating gcode in ", so.get_filename()
        self.robot_spec.write_calibration_gcode(so.get_filename() )
         
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
