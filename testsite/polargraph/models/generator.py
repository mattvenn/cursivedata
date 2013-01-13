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
import jsonfield


#Points to some code and associated parameters which are needed to process data
#This is not an actual running generator, but an template to make new real generators
class Generator( models.Model ) :
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000,default="Unknown")
    image = models.CharField(max_length=200,default="No Image")
    file_path = models.CharField(max_length=200,default="./scripts")
    module_name = models.CharField(max_length=200)
    module = None
    def init(self) :
        self.module = self.get_file( self.module_name )
        for param in self.module.get_params():
            self.add_or_update_param( param )
        return
    #Processes a given chunk of data to return some SVG
    def process_data( self, svg_document, data, params, state ) :
        return self.module.process(svg_document, data,params,state)
    
    #Checks to see if the current data is enough to run
    def can_run( self, data, params, state ) :
        return self.module.can_run(data,params,state)
    
    def __unicode__(self):
        return self.name
    @staticmethod
    def create_from_file(module_name) :
        mod = Generator.get_file( module_name )
        g = Generator( name=mod.get_name(), description=mod.get_description(), module_name=module_name )
        g.save()
        for p in mod.get_params() :
            param = Parameter( name=p["name"], default=p["default"] )
            g.parameter_set.add( param )
            param.save()
        return g
            
    @staticmethod
    def get_file(module_name) : #No error checking yet!))
        f, filename, data = find_module(module_name, ["./scripts"])
        return load_module(module_name, f, filename, data)

    def get_state( self ) :
        s = GeneratorState( name=self.name, generator=self )
        s.save()
        for p in self.parameter_set.all():
            s.params[p.name] = p.default
        return s
    
    def add_or_update_param(self,param_spec):
        try:
            pr = self.get_param(param_spec['name'])
        except Exception:
            pr = Parameter(generator=self)
        pr.name=param_spec['name']
        pr.default=param_spec.get('default',0)
        pr.save()
        
    def get_param(self,name):
        pr = self.parameter_set.get(name=name)
        if pr.count() > 0:
            return pr.get(0)
        return None
            
    
    class Meta:
        app_label = 'polargraph'

#Generators have parameters. These can result in UI elements
class Parameter( models.Model ) :
    name = models.CharField(max_length=200)
    default = models.FloatField(default=0,blank=True)
    description = models.CharField(default="Some parameter",blank=True,max_length=1000)
    generator = models.ForeignKey( Generator )
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'polargraph'

#This is a running instance of a generator. It has parameter values and a Dict to store internal state
class GeneratorState( models.Model ):
    name = models.CharField(max_length=200)
    generator = models.ForeignKey( Generator )
    params = jsonfield.JSONField(default={})
    state = models.CharField(max_length=20000,default=json.dumps({"internal":"state"}))
    
    def __init__(self, *args, **kwargs):
        super(GeneratorState, self).__init__(*args, **kwargs)
        self.update()

    def update(self) :
        for p in self.generator.parameter_set.all() :
            if not self.params.has_key(p.name):
                self.params[p.name] = p.default
        
    def __unicode__(self):
        return self.name
    
    def read_internal_state(self) :
        return json.loads( self.state )
    
    def write_state( self, obj ) :
        self.state = json.dumps( obj )

    class Meta:
        app_label = 'polargraph'
