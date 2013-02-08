'''
Created on 12 Jan 2013

@author: dmrust
'''

import traceback
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
from polargraph.models.drawing_state import DrawingState,StoredOutput
import pysvg.structure
import pysvg.builders
from django.utils.datetime_safe import datetime
import shutil
import time
import os

from polargraph.drawing import Drawing



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
        print "Pipeline updating"
        data = data or self.data_store
        print "Getting params"
        params = self.state.params
        print "Getting internal state"
        internal_state = self.state.state
        print "Generator init"
        try:
            self.generator.init()
        except Exception as e:
            print "Couldn't init generator:",e
        print "Asking generator if it can run"
        if self.generator.can_run( data, params, internal_state ):
            print "Generator running"
            try:
                #Create a new document to write to
                svg_document = self.create_svg_doc()
                self.generator.process_data( Drawing(svg_document), data, params, internal_state )
                self.state.save()
                data.clear_current()
                self.add_svg( svg_document )
                print "Generator run OK!"
            except Exception as e:
                print "Problem running generator",self,e    
                print traceback.format_exc()
        else:
            print "Generator not ready to run"
    
    def begin(self):
        self.reset();
        self.generator.init()
        try:
            svg_document = self.create_svg_doc()
            self.generator.begin_drawing( Drawing(svg_document), self.state.params, self.state.state )
            self.state.save()
            self.add_svg( svg_document )
        except Exception as e:
            print "Couldn't begin document:",e
    
    def end(self):
        self.generator.init()
        try:
            svg_document = self.create_svg_doc()
            self.generator.end_drawing( Drawing(svg_document), self.state.params, self.state.state )
            self.state.save()
            self.add_svg( svg_document )
        except Exception as e:
            print "Couldn't end document:",e
 

    def add_svg(self, svg_document ):
        super(Pipeline, self).add_svg(svg_document)
        print str(self)," sending data from ",str(self.generator),"to endpoint", str(self.endpoint)
        self.endpoint.input_svg( self.last_svg_file,self)
    
    def reset(self):
        super(Pipeline, self).reset()
        self.data_store.clear_all()
        self.state.write_state({})
        self.state.save()
        
    def get_output_name(self):
        return "pipeline"

    def get_stored_output(self,output_type,status):
        try:
            return StoredOutput.objects.get(endpoint=self.endpoint,pipeline=self,generator=self.generator,run_id=self.run_id,filetype=output_type,status=status)
        except:
            return StoredOutput(endpoint=self.endpoint,pipeline=self,generator=self.generator,run_id=self.run_id,filetype=output_type,status=status)
        
    class Meta:
        app_label = 'polargraph'
        

