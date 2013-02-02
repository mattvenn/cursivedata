'''
Created on 2 Feb 2013

@author: dmrust
'''
from django.db import models
import polargraph.svg as svg
import pysvg.structure
import pysvg.builders
from django.utils.datetime_safe import datetime
import shutil
import os

'''
DrawingState is a class which deals with drawings that change incrementally over time. It:
* maintains a current drawing and a drawing with the last bit which was added
* converts everything from SVG into PNG
* adds to a history of drawings (StoredOutput) which can then be looked up 
'''
class DrawingState( models.Model ):
    run_id = models.IntegerField(default=0)
    last_updated = models.DateTimeField("Last Updated",default=datetime.now())
    full_svg_file = models.CharField(max_length=200,blank=True)
    last_svg_file = models.CharField(max_length=200,blank=True)
    full_image_file = models.CharField(max_length=200,blank=True)
    last_image_file = models.CharField(max_length=200,blank=True)
    img_width = models.IntegerField(default=500)
    img_height = models.IntegerField(default=500)
    
    #Adds a chunk of SVG to this drawing
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

    #Change ths size of the drawing    
    def update_size(self,width,height):
        changed = self.img_width != width or self.img_height != height
        self.img_width = width
        self.img_height = height
        if changed:
            self.reset()
        
    #Creates a blank svg file with the given filename
    def create_blank_svg(self,filename):
        doc = self.create_svg_doc(self.img_width, self.img_height, True)
        doc.save(filename)
    
    #Create an empty svg doc with the given width and height
    def create_svg_doc(self,width,height,createRect=False):
        #Should specify mm for document size
        widthmm = "%fmm" % width
        heightmm = "%fmm" % height
        doc = pysvg.structure.svg(width=widthmm,height=heightmm)
        doc.set_viewBox("0 0 %s %s" % (width, height))
        if createRect:
            build = pysvg.builders.ShapeBuilder()
            doc.addElement(build.createRect(0, 0, width="100%", height="100%", fill = "rgb(255, 255, 255)"))
        return doc
        
    #Updates the full image, by creating a PNG from the full SVG, and storing the SVG and PNG in the history
    def update_full_image(self):
        self.full_image_file = self.get_full_image_filename()
        self.store_output("complete", self.full_svg_file, self.full_image_file)
        
    #Updates the partial image, by creating a PNG from the partial SVG, and storing the SVG and PNG in the history
    def update_latest_image(self):
        self.last_image_file = self.get_partial_image_filename()
        self.store_output("partial", self.last_svg_file, self.last_image_file)
        
    #Converts the SVG into PNG, and stores them both in a StoredOutput if appropriate
    def store_output(self,status,svg_file,image_file):
        svg.convert_svg_to_png(svg_file, image_file)
        png_store = self.get_stored_output("png", status)
        svg_store = self.get_stored_output("svg", status)
        if png_store :
            png_store.set_file(image_file)
        if svg_store :
            svg_store.set_file(svg_file)
    
    #Gets a stored output for this object and type of output. It should take into account run_id
    #and return the *same* stored output when called again in a single run - this means that
    #only one output (of each kind) will be stored each run.
    def get_stored_output(self,output_type,state):
        return None
    
    #Makes sure that self.full_svg_file points to a valid SVG document
    #If forced, it will create a blank one even if it exists
    def ensure_full_document(self,force=False):
        if self.full_svg_file is None or self.full_svg_file == "" or force:
            self.full_svg_file = self.get_full_svg_filename()
            self.create_blank_svg(self.full_svg_file)
            self.update_full_image()
            
    #Clears the latest image file
    def clear_latest_image(self):
        self.last_svg_file = self.get_partial_svg_filename()
        self.create_blank_svg(self.last_svg_file)
        self.update_latest_image()
        self.save()
            
    #Increments the run_id and starts a new blank document
    def reset(self):
        self.run_id = self.run_id + 1
        self.ensure_full_document(True)
        self.clear_latest_image()
        self.save()
    
    #Filenames for storing various kinds of output
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
    
    class Meta:
        abstract = True

class StoredOutput( models.Model ):
    endpoint = models.ForeignKey( "Endpoint", blank=True, null=True )
    pipeline = models.ForeignKey( "Pipeline", blank=True, null=True )
    generator = models.ForeignKey( "Generator", blank=True, null=True )
    run_id = models.IntegerField(default=0)
    filetype = models.CharField(max_length=10,default="unknown") #svg or png
    status = models.CharField(max_length=10,default="complete") #complete or partial
    filename = models.CharField(max_length=200,default="output/none")
    modified = models.DateTimeField(auto_now=True)
    
    def set_file(self,fn):
        base,extension = os.path.splitext(fn)
        if extension != "."+self.filetype:
            print "Warning: got a "+extension+", but was expecting a "+self.filetype
        self.filename = self.get_filename()
        shutil.copy2(fn,self.filename)
        self.save()
    
    def get_filename(self):
        if not self.id > 0:
            self.save()
        return "data/output/"+str(self.id)+"_"+self.status+"."+self.filetype
        
    class Meta:
        app_label = 'polargraph'
        