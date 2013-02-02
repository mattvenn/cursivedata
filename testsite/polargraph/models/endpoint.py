'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
import polargraph.svg as svg
from polargraph.models.pipeline import StoredOutput
from polargraph.models.drawing_state import DrawingState
import pysvg.structure
import pysvg.builders
from pysvg.parser import parse



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
    url = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        super(Endpoint, self).__init__(*args, **kwargs)
        #Set the actual size of the drawing area based on the size of the robot and the margins
        self.img_width = self.width - self.side_margin * 2
        self.img_height = self.height - self.top_margin
        #Not sure this is used
        self.x_min = self.side_margin
        self.y_min = self.top_margin
        self.x_max = self.side_margin + self.available_x
        self.y_max = self.top_margin + self.available_y
   
   
    def input_svg(self,svg_file, pipeline ):
        print "Adding SVG"
        try:
            current_drawing = self.transform_svg(svg_file,pipeline)
            print current_drawing.getXML()
            self.add_svg(current_drawing)
            self.create_gcode(self.last_svg_file)
        except Exception as e:
            print "Problem updating SVG in endpoint:",e
    
    def create_gcode(self,svg_file):
        try:
            so = GCodeOutput(endpoint=self)
            so.save()
            svg.convert_svg_to_gcode(self,self.last_svg_file,so.get_filename())
        except Exception as e:
            print "Coudldn't make GCode:",e
            so.delete()
            
    def transform_svg(self, svg_file, pipeline):
        current_drawing = self.create_svg_doc( self.img_width, self.img_height )
        try:
            svg_data = parse(svg_file)
            xoffset = pipeline.print_top_left_x
            yoffset = pipeline.print_top_left_y
            scale = pipeline.print_width / pipeline.img_width
            tr = pysvg.builders.TransformBuilder()
            tr.setScaling(scale)
            trans = str(xoffset) + " " + str(yoffset) 
            tr.setTranslation( trans )
            group = pysvg.structure.g()
            print "Transform:"+tr.getTransform()
            group.set_transform(tr.getTransform())
            for element in svg_data.getAllElements():
                group.addElement(element)
            current_drawing.addElement(group)
            return current_drawing
        except Exception as e:
            print "Couldn't read SVG file passed in:",svg_file,e        
                
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
        
    def get_stored_output(self,output_type,status):
        try:
            return StoredOutput.objects.get(endpoint=self,pipeline=None,generator=None,run_id=self.run_id,filetype=output_type,status=status)
        except:
            return StoredOutput(endpoint=self,pipeline=None,generator=None,run_id=self.run_id,filetype=output_type,status=status)
      
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
    
    class Meta:
        app_label = 'polargraph'
