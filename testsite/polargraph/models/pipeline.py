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
from polargraph.models.cosm import COSMSource



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
    print_width = models.FloatField( default=500 )

    def __init__(self, *args, **kwargs):
        super(Pipeline, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.name

    #Executes the pipeline by running the generator on the next bit of data
    #Not sure why we need to pass the data object in, but using self.data_store gives funny results
    def update( self, data=None ) :
        data = data or self.data_store
        params = self.state.params
        internal_state = self.state.state
        print "Asking generator if it can run"
        if self.generator.can_run( data, params, internal_state ):
            #Create a new document to write to
            svg_document = self.create_svg_doc()
            self.generator.process_data( Drawing(svg_document), data, params, internal_state )
            self.state.save()
            data.clear_current()
            if len(svg_document.getXML()) == 0:
                print "!!! found empty XML"
                import pdb; pdb.set_trace()
#            if self.id == 4:
#                import pdb; pdb.set_trace()
#                print svg_document.getXML()
            try:
                self.add_svg( svg_document )
            except Exception:
                #import pdb; pdb.set_trace()
                pass
            self.generator.update_last_used()
            print "Generator run OK!"
        else:
            print "Generator not ready to run"
    
    def begin(self):
        self.reset();
        svg_document = self.create_svg_doc()
        self.generator.begin_drawing( Drawing(svg_document), self.state.params, self.state.state )
        self.state.save()
        self.add_svg( svg_document )
    
    def end(self):
        svg_document = self.create_svg_doc()
        self.generator.end_drawing( Drawing(svg_document), self.state.params, self.state.state )
        self.state.save()
        self.add_svg( svg_document )
 

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
        except StoredOutput.DoesNotExist:
            # XXX: The new object isn't saved. Is this intentional?
            return StoredOutput(endpoint=self.endpoint,pipeline=self,generator=self.generator,run_id=self.run_id,filetype=output_type,status=status)
    
    #Gets recent output which is not the current run
    def get_recent_output(self,start=0,end=8):
        return StoredOutput.objects \
                .order_by('-modified') \
                .filter(pipeline=self,status="complete",filetype="svg") \
                .exclude(run_id= self.run_id)[start:end]
    """
    #Gets all the cosm triggers on this pipeline
    def get_cosm_triggers(self):
        return COSMSource.objects.filter(data_store=self.data_store)
    """
    
    #Gets the current values for all parameters as a dict
    def get_param_dict(self):
        return self.generator.get_param_dict( self.state.params )
        
    #Sets up a datastore and generator state for use
    def init_data(self,force=False,save=True):
        """
        if (not self.data_store_id) or force:
            ds = DataStore(name="Data for"+str(self.name))
            ds.save()
            self.data_store = ds
        """
        if (not self.state_id) or force :
            gs = GeneratorState(name="Data for"+str(self.name), generator=self.generator)
            gs.save()
            self.state = gs
        if save:
            self.last_updated = timezone.now()
            self.save()
        
    def save(self, *args, **kwargs):
        if not self.pk:
            self.init_data(save=False)
        super(Pipeline, self).save(*args, **kwargs)
    class Meta:
        app_label = 'polargraph'
        

