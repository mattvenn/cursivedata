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
#import cursivedata.svg as svg
import cursivelib.svg as svg
import requests
import cursivedata.models.cosm
from cursivedata.models.generator import Generator,GeneratorState
from cursivedata.models.data import DataStore
from cursivedata.models.drawing_state import DrawingState,StoredOutput
import pysvg.structure
import pysvg.builders
from django.utils.datetime_safe import datetime
import shutil
import time
import os

from cursivedata.drawing import Drawing
from cursivedata.models.cosm import COSMSource



#A complete pipeline from data source through to a running algorithm
class Pipeline( DrawingState ) :
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000,default="",blank=True)
    generator = models.ForeignKey( Generator)
    data_store = models.OneToOneField( DataStore)
    state = models.OneToOneField( GeneratorState)
    endpoint = models.ForeignKey( "Endpoint")
    paused = models.BooleanField(default=False)
    sources = models.ManyToManyField(COSMSource, through=COSMSource.pipelines.through, blank=True)

    print_top_left_x = models.FloatField(default=0)
    print_top_left_y = models.FloatField(default=0)
    print_width = models.FloatField( default=500 )

    auto_begin_days = models.IntegerField( default=0 )
    next_auto_begin_date = models.DateTimeField( blank=True,null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.init_data(save=False)
        super(Pipeline, self).save(*args, **kwargs)


    def __unicode__(self):
        return self.name

    def resume(self):
        self.paused = False
        self.save()
        self.update()

    def pause(self):
        self.paused = True
        self.save()

    #Might be able to move some of this here from DataStore in the future
    def add_data(self,data):
        self.data_store.add_data(data)

    #Executes the pipeline by running the generator on the next bit of data
    #Not sure why we need to pass the data object in, but using self.data_store gives funny results
    def update( self, data=None ) :
        if self.paused:
            print "pipeline paused"
            return
        #check if we need to do an auto begin
        if self.auto_begin_days:
            #might need to initialise
            if self.next_auto_begin_date == None:
                #set to tomorrow
                now = timezone.now()
                self.next_auto_begin_date = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0)+timezone.timedelta(days=1)
                self.save()
            #if it's time to auto begin
            elif timezone.now() > self.next_auto_begin_date:
                #update the next auto time
                self.next_auto_begin_date = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0)+timezone.timedelta(days=self.auto_begin_days)
                self.save()
                print ">>>pipeline", self.name, " auto begin"
                self.begin()

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
                #import pdb; pdb.set_trace()
#            if self.id == 4:
#                import pdb; pdb.set_trace()
#                print svg_document.getXML()
            self.add_svg( svg_document )
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
    def get_recent_output(self,start=0,end=3):
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
        if (not self.data_store_id) or force:
            ds = DataStore(name=str(self.name)+" datastore")
            ds.save()
            self.data_store = ds
        if (not self.state_id) or force :
            gs = GeneratorState(name="generator state for "+str(self.name), generator=self.generator)
            gs.save()
            self.state = gs
        if save:
            self.last_updated = timezone.now()
            self.save()
        
    class Meta:
        app_label = 'cursivedata'
        

