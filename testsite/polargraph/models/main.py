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


#A complete pipeline from data source through to a running algorithm
class Pipeline( models.Model ) :
    name = models.CharField(max_length=200)
    generator = models.OneToOneField( Generator )
    data_store = models.OneToOneField( DataStore )
    state = models.OneToOneField( GeneratorState )
    endpoint = models.ForeignKey( Endpoint )
    current_image = models.CharField(max_length=200)
    last_updated = models.DateTimeField("Last Updated")
    full_svg_file = models.CharField(max_length=200,blank=True)
    def __unicode__(self):
        return self.name

    #Executes the pipeline by running the generator on the next bit of data
    def update( self ) :
        params = self.state.params_to_dict();
        internal_state = self.state.read_internal_state()
        self.generator.init()
        if self.generator.can_run( self.data_store, params, internal_state ):
            svg_string = self.generator.process_data( self.data_store, params, internal_state )
            print "Pipeline got data", str( svg_string )
            
            self.data_store.clear_current()
            self.state.write_state(internal_state)
            self.state.save()
            
            svg_file = svg.write_temp_svg_file(svg_string)
            print "Pipeline Got SVG file:",svg_file
            
            if self.full_svg_file is None or self.full_svg_file == "":
                self.full_svg_file = svg.get_temp_filename("svg")
                self.save
                
            # Add SVG to full output history
            print "Pipeline got SVG file:",svg_file,", Appending to:",self.full_svg_file
            svg.append_svg_to_file( svg_file, self.full_svg_file )
        
            self.endpoint.add_svg( svg_file )
            print str(self),"using",str(self.generator),"to send to endpoint", str(self.endpoint)
            return svg;
        return ""

    class Meta:
        app_label = 'polargraph'