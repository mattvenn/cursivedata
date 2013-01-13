'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from imp import find_module, load_module
import json
import csv
import polargraph.svg as svg
import requests
import polargraph.models.cosm
from polargraph.models.generator import Generator,GeneratorState
from polargraph.models.data import DataStore
from polargraph.models.endpoint import Endpoint
import pysvg.structure
import pysvg.builders
from django.utils.datetime_safe import datetime


#A complete pipeline from data source through to a running algorithm
class Pipeline( models.Model ) :
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000,default="",blank=True)
    generator = models.OneToOneField( Generator )
    data_store = models.OneToOneField( DataStore )
    state = models.OneToOneField( GeneratorState )
    endpoint = models.ForeignKey( Endpoint )
    last_updated = models.DateTimeField("Last Updated")
    full_svg_file = models.CharField(max_length=200,blank=True)
    last_svg_file = models.CharField(max_length=200,blank=True)
    full_image_file = models.CharField(max_length=200,blank=True)
    last_image_file = models.CharField(max_length=200,blank=True)
    img_width = models.IntegerField(default=500)
    img_height = models.IntegerField(default=500)
    def __unicode__(self):
        return self.name
    def __init__(self, *args, **kwargs):
        super(Pipeline, self).__init__(*args, **kwargs)
        self.ensure_full_document()
    
    #Executes the pipeline by running the generator on the next bit of data
    #Not sure why we need to pass the data object in, but using self.data_store gives funny results
    def update( self, data=None ) :
        data = data or self.data_store
        params = self.state.params_to_dict();
        internal_state = self.state.read_internal_state()
        self.generator.init()
        print "Pipeline Data:",self.data_store.get_current()
        print "Data:",data.get_current()
        print "Pipeline DataID:",self.data_store_id
        print "Pipeline DHash:",hash(self.data_store)
        if self.generator.can_run( data, params, internal_state ):
            #Create a new document to write to
            svg_document = pysvg.structure.svg(width=self.img_width,height=self.img_height)
            self.generator.process_data( svg_document, data, params, internal_state )
            
            data.clear_current()
            self.state.write_state(internal_state)
            self.state.save()
            
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
            #Send to endpoint
            self.endpoint.add_svg( self.last_svg_file )
            print str(self),"using",str(self.generator),"to send to endpoint", str(self.endpoint)
            self.last_updated = datetime.now()
            self.save()
    
    def get_partial_svg_filename(self):
        return svg.get_temp_filename("svg")
    def get_full_svg_filename(self):
        return svg.get_temp_filename("svg")
    def get_partial_image_filename(self):
        return svg.get_temp_filename("png")
    def get_full_image_filename(self):
        return svg.get_temp_filename("png")
    def create_blank_svg(self,filename):
        doc = pysvg.structure.svg(width=self.img_width,height=self.img_height)
        build = pysvg.builders.ShapeBuilder()
        doc.addElement(build.createRect(0, 0, width="100%", height="100%", fill = "rgb(255, 255, 255)"))
        doc.save(filename)
    def update_full_image(self):
        self.full_image_file = self.get_full_image_filename()
        svg.convert_svg_to_png(self.full_svg_file, self.full_image_file)
        
    def update_latest_image(self):
        self.last_image_file = self.get_partial_image_filename()
        svg.convert_svg_to_png(self.last_svg_file, self.last_image_file)
    
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
        self.ensure_full_document(True)
        self.clear_latest_image()
        self.data_store.clear_all()
        self.state.write_state({})
        self.state.save()
        self.save()

    class Meta:
        app_label = 'polargraph'