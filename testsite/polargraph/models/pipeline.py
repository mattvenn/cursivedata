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
from polargraph.models.drawing_state import DrawingState
import pysvg.structure
import pysvg.builders
from django.utils.datetime_safe import datetime
import shutil
import time
import os




#A complete pipeline from data source through to a running algorithm
class Pipeline( DrawingState ) :
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000,default="",blank=True)
    generator = models.ForeignKey( Generator)
    data_store = models.OneToOneField( DataStore)
    state = models.OneToOneField( GeneratorState)
    endpoint = models.ForeignKey( "Endpoint")

    print_top_left_x = models.FloatField(default=0)
    print_top_left_y = models.FloatField(default=0)
    print_width = models.FloatField( default=200 )
    
    def __unicode__(self):
        return self.name
    def __init__(self, *args, **kwargs):
        super(Pipeline, self).__init__(*args, **kwargs)
        try:
            self.ensure_full_document()
        except Exception as e:
            print "Coudln't make document ",e
    
    #Executes the pipeline by running the generator on the next bit of data
    #Not sure why we need to pass the data object in, but using self.data_store gives funny results
    def update( self, data=None ) :
        data = data or self.data_store
        params = self.state.params
        internal_state = self.state.state
        self.generator.init()
        if self.generator.can_run( data, params, internal_state ):
            #Create a new document to write to
            svg_document = pysvg.structure.svg(width=self.img_width,height=self.img_height)
            self.generator.process_data( svg_document, data, params, internal_state )
            self.state.save()
            data.clear_current()
            self.add_svg( svg_document )
        
    def add_svg(self, svg_document ):
        super(Pipeline, self).add_svg(svg_document)
        print str(self)," sending data from ",str(self.generator),"to endpoint", str(self.endpoint)
        self.endpoint.add_svg( self.last_svg_file,self)
    
    def reset(self):
        super(Pipeline, self).reset()
        self.data_store.clear_all()
        self.state.write_state({})
        self.state.save()
        
    def get_output_name(self):
        return "pipeline"

    def get_stored_output(self,output_type,state):
        return StoredOutput.get_output(self, output_type, state)
        
    class Meta:
        app_label = 'polargraph'
        

class StoredOutput( models.Model ):
    endpoint = models.ForeignKey( "Endpoint", blank=True, null=True )
    pipeline = models.ForeignKey( Pipeline, blank=True, null=True )
    generator = models.ForeignKey( Generator, blank=True, null=True )
    run_id = models.IntegerField(default=0)
    filetype = models.CharField(max_length=10,default="unknown") #svg or png
    status = models.CharField(max_length=10,default="complete") #complete or partial
    filename = models.CharField(max_length=200,default="output/none")
    modified = models.DateTimeField(auto_now=True)
    
    @staticmethod
    def get_output(pipeline,filetype,status):
        try:
            return StoredOutput.objects.get(endpoint=pipeline.endpoint,pipeline=pipeline,generator=pipeline.generator,run_id=pipeline.run_id,filetype=filetype,status=status)
        except:
            return StoredOutput(endpoint=pipeline.endpoint,pipeline=pipeline,generator=pipeline.generator,run_id=pipeline.run_id,filetype=filetype,status=status)
        
        
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
