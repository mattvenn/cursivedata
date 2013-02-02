'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
import polargraph.svg as svg
from polargraph.models.pipeline import StoredOutput
import requests
import pysvg.structure
import pysvg.builders
from pysvg.parser import parse
from django.utils.datetime_safe import datetime



#A Robot, or other output device
class Endpoint( models.Model ):
    name = models.CharField(max_length=200)
    device = models.CharField(max_length=200)
    width = models.FloatField(max_length=200)
    side_margin = models.FloatField(max_length=200)
    top_margin = models.FloatField(max_length=200)
    height = models.FloatField(max_length=200)
    full_svg_file = models.CharField(max_length=200,blank=True)
    last_svg_file = models.CharField(max_length=200,blank=True)
    paused = models.BooleanField(default=False)
    #add this to db, using url for now
    status = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    run_id = models.IntegerField(default=0)
    last_updated = models.DateTimeField("Last Updated",default=datetime.now())
    
    def add_svg(self,svg_file, generator_params, pipeline ):
        print "Adding SVG"
        try:
            #Should specify mm for document size
            widthmm = "%fmm" % self.width
            heightmm = "%fmm" % self.height

            current_drawing = pysvg.structure.svg(width=widthmm,height=heightmm)
            #Should do transforming here
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
            except Exception as e:
                print "Couldn't read SVG file passed in:",svg_file,e
                
            #Save the partial file and make a PNG of it
            self.last_svg_file = self.get_partial_svg_filename()
            current_drawing.save(self.last_svg_file)
            self.update_latest_image()
                
            print "Saved update as:",self.last_svg_file
            self.ensure_full_document()
                
            # Add SVG to full output history
            svg.append_svg_to_file( self.last_svg_file, self.full_svg_file )
            self.update_full_image()  
            
            so = GCodeOutput(endpoint=self)
            so.save()
            svg.convert_svg_to_gcode(self,generator_params,self.last_svg_file,so.get_filename())
            self.last_updated = datetime.now()
            self.save()
        except Exception as e:
            print "Problem updating SVG in endpoint:",e
        
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

    def get_next(self):
        try:
            return GCodeOutput.objects.filter(endpoint=self,served=False).order_by('modified')[:1].get()
        except Exception as e:
            return None
        
    def consume(self):
        n = self.get_next( );
        n.served = True;
        n.save()
    def update_size(self,width,height):
        changed = self.img_width != width or self.img_height != height
        self.img_width = width
        self.img_height = height
        if changed:
            self.reset()
                  
    def create_blank_svg(self,filename):
        doc = pysvg.structure.svg(width=self.width,height=self.height)
        build = pysvg.builders.ShapeBuilder()
        doc.addElement(build.createRect(0, 0, width="100%", height="100%", fill = "rgb(255, 255, 255)"))
        doc.save(filename)
    
    def update_full_image(self):
        print "Update latest image"
        #self.full_image_file = self.get_full_image_filename()
        #svg.convert_svg_to_png(self.full_svg_file, self.full_image_file)
        #StoredOutput.get_output(self, "png", "complete").set_file(self.full_image_file)
        self.get_stored_output().set_file(self.full_svg_file)
        
    def update_latest_image(self):
        print "Update latest image"
        #self.last_image_file = self.get_partial_image_filename()
        #svg.convert_svg_to_png(self.last_svg_file, self.last_image_file)
        #StoredOutput.get_output(self, "png", "partial").set_file(self.last_image_file)
        #StoredOutput.get_output(self, "svg", "partial").set_file(self.last_svg_file)
    
    def ensure_full_document(self,force=False):
        if self.full_svg_file is None or self.full_svg_file == "" or force:
            self.full_svg_file = self.get_full_svg_filename()
            self.create_blank_svg(self.full_svg_file)
            self.update_full_image()
            
    def clear_latest_image(self):
        self.last_svg_file = self.get_partial_svg_filename()
        self.create_blank_svg(self.last_svg_file)
        self.update_latest_image()
        self.save()
    
    def resume(self):
        self.paused = False
        self.save()

    def pause(self):
        self.paused = True
        self.save()
        
    def reset(self):
        self.run_id = self.run_id + 1
        self.ensure_full_document(True)
        self.clear_latest_image()
        self.save()
        
    def get_stored_output(self):
        try:
            return StoredOutput.objects.get(endpoint=self,pipeline=None,generator=None,run_id=self.run_id,filetype="svg",status="complete")
        except:
            return StoredOutput(endpoint=self,pipeline=None,generator=None,run_id=self.run_id,filetype="svg",status="complete")

        
    def get_partial_svg_filename(self):
        return self.get_filename("partial", "svg")
    def get_full_svg_filename(self):
        return self.get_filename("complete", "svg")
    def get_filename(self,status,extension):
        if not self.id > 0:
            self.save()
        return "data/working/endpoint"+str(self.id)+"_"+status+"."+extension
      
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
