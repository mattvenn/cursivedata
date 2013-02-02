'''
Created on 2 Feb 2013

@author: dmrust
'''
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import polargraph.svg as svg
import pysvg.structure
import pysvg.builders
from django.utils.datetime_safe import datetime

class DrawingState( models.Model ):
    run_id = models.IntegerField(default=0)
    last_updated = models.DateTimeField("Last Updated",default=datetime.now())
    full_svg_file = models.CharField(max_length=200,blank=True)
    last_svg_file = models.CharField(max_length=200,blank=True)
    full_image_file = models.CharField(max_length=200,blank=True)
    last_image_file = models.CharField(max_length=200,blank=True)
    img_width = models.IntegerField(default=500)
    img_height = models.IntegerField(default=500)
    
    def add_svg(self, svg_document ):
        #Save the partial file and make a PNG of it
        self.last_svg_file = self.get_partial_svg_filename()
        svg_document.save(self.last_svg_file)
        self.update_latest_image()
        print "Saved update as:",self.last_image_file
        self.ensure_full_document()
        # Add SVG to full output history
        svg.append_svg_to_file( self.last_svg_file, self.full_svg_file )
        self.update_full_image()
        print "Saved whole image as:",self.full_image_file
        self.last_updated = datetime.now()
        self.save()

    def get_partial_svg_filename(self):
        return self.get_filename("partial", "svg")
    def get_full_svg_filename(self):
        return self.get_filename("complete", "svg")
    def get_partial_image_filename(self):
        return self.get_filename("partial", "png")
    def get_full_image_filename(self):
        return self.get_filename("complete", "png")
    def get_filename(self,status,extension):
        if not self.id > 0:
            self.save()
        return "data/working/"+self.get_output_name()+"_"+str(self.id)+"_"+status+"."+extension
    def get_output_name(self):
        return "unknown"
        
    def update_size(self,width,height):
        changed = self.img_width != width or self.img_height != height
        self.img_width = width
        self.img_height = height
        if changed:
            self.reset()
        
    def create_blank_svg(self,filename):
        doc = pysvg.structure.svg(width=self.img_width,height=self.img_height)
        build = pysvg.builders.ShapeBuilder()
        doc.addElement(build.createRect(0, 0, width="100%", height="100%", fill = "rgb(255, 255, 255)"))
        doc.save(filename)
        
    def update_full_image(self):
        self.full_image_file = self.get_full_image_filename()
        svg.convert_svg_to_png(self.full_svg_file, self.full_image_file)
        full_png = self.get_stored_output("png", "complete")
        full_svg = self.get_stored_output("svg", "complete")
        if full_png:
            full_png.set_file(self.full_image_file)
        if full_svg:
            full_svg.set_file(self.full_svg_file)
        
    def update_latest_image(self):
        self.last_image_file = self.get_partial_image_filename()
        svg.convert_svg_to_png(self.last_svg_file, self.last_image_file)
        partial_png = self.get_stored_output("png", "partial")
        partial_svg = self.get_stored_output("svg", "partial")
        if partial_png :
            partial_png.set_file(self.last_image_file)
        if partial_svg :
            partial_svg.set_file(self.last_svg_file)
    
    def get_stored_output(self,output_type,state):
        return None
    
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
            
    def reset(self):
        self.run_id = self.run_id + 1
        self.ensure_full_document(True)
        self.clear_latest_image()
        self.save()
        
    class Meta:
        abstract = True
        