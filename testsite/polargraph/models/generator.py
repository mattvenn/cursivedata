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
            ps = GeneratorStateParameter( parameter=p, state=s, value=p.default )
            ps.save()
        return s
    
    class Meta:
        app_label = 'polargraph'

#Generators have parameters. These can result in UI elements
class Parameter( models.Model ) :
    name = models.CharField(max_length=200)
    default = models.FloatField(default=0,blank=True)
    generator = models.ForeignKey( Generator )
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'polargraph'

#This is a running instance of a generator. It has parameter values and a Dict to store internal state
class GeneratorState( models.Model ):
    name = models.CharField(max_length=200)
    generator = models.ForeignKey( Generator )
    params = {}
    state = models.CharField(max_length=20000,default=json.dumps({"internal":"state"}))

    def update(self) :
        for p in self.generatorstateparameter_set:
            self.params[p.parameter.name] = p
        
    def get_param(self,name) :
        self.update() #Ugly - find a better way when Dave understands the database model better
        return self.params[name].value
    
    def __unicode__(self):
        return self.name
    
    def read_internal_state(self) :
        st = self.state
        print "State::",st,"::"
        print "Loaded: ",json.loads( st )
        return json.loads( st )
    
    def write_state( self, obj ) :
        self.state = json.dumps( obj )

    def params_to_dict(self) :
        state = {}
        for p in self.generatorstateparameter_set.all():
            state[p.parameter.name] = p.value
        return state
    def params_from_dict(self,data):
        self.update()
        for (key,value) in data.iteritems() :
            self.params[key].value = value

    class Meta:
        app_label = 'polargraph'

#Parameter values for a given GeneratorState
class GeneratorStateParameter( models.Model ):
    parameter = models.ForeignKey( Parameter )
    state = models.ForeignKey( GeneratorState )
    value = models.FloatField()
    def __unicode__(self):
        return self.parameter.name+"="+str(self.value)

    class Meta:
        app_label = 'polargraph'