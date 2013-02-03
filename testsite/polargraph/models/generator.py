'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
from imp import find_module, load_module
import jsonfield
from polargraph.models.drawing_state import StoredOutput
from django.utils.datetime_safe import datetime


#Points to some code and associated parameters which are needed to process data
#This is not an actual running generator, but an template to make new real generators
class Generator( models.Model ) :
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000,default="Unknown")
    image = models.CharField(max_length=200,default="No Image")
    file_path = models.CharField(max_length=200,default="./generators")
    module_name = models.CharField(max_length=200)
    last_updated = models.DateTimeField("Last Updated",default=datetime.now())
    last_used = models.DateTimeField("Last Used",default=datetime.now())
    
    module = None
    def __init__(self, *args, **kwargs):
        super(Generator, self).__init__(*args, **kwargs)
        try:
            self.module = self.get_file( self.module_name )
            for param in self.module.get_params():
                self.add_or_update_param( param )
        except Exception as e:
            print "Coudln't update Generator params:",e
        return
    #Processes a given chunk of data to return some SVG
    def process_data( self, svg_document, data, params, state ) :
        return self.module.process(svg_document, data,params,state)
    
    #Checks to see if the current data is enough to run
    def can_run( self, data, params, state ) :
        return self.module.can_run(data,params,state)
    
    #Processes a given chunk of data to return some SVG
    def begin_drawing( self, svg_document, params, state ) :
        return self.module.begin(svg_document, params,state)
    
    #Processes a given chunk of data to return some SVG
    def end_drawing( self, svg_document, params, state ) :
        return self.module.end(svg_document, params,state)
    
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
        f, filename, data = find_module(module_name, ["./generators"])
        return load_module(module_name, f, filename, data)

    def get_state( self ) :
        s = GeneratorState( name=self.name, generator=self )
        s.save()
        for p in self.parameter_set.all():
            s.params[p.name] = p.default
        return s
    
    def add_or_update_param(self,param_spec):
        pr = self.get_param(param_spec['name'])
        if not pr:
            pr = Parameter(generator=self)
        pr.name=param_spec['name']
        pr.default=param_spec.get('default',param_spec.get('default',0))
        pr.description=param_spec.get('description',param_spec.get('description',"Unknown"))
        pr.save()
        
    def get_param(self,name):
        #Should be doing a proper query here!
        for p in self.parameter_set.all():
            if p.name == name:
                return p
        return None
    def get_recent_output(self,start=0,end=8):
        return StoredOutput.objects.order_by('-modified').filter(generator=self,status="complete",filetype="svg")[start:end]            
    
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
    state = jsonfield.JSONField(default={})
    
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
        return self.state
    
    def write_state( self, obj ) :
        self.state = obj

    class Meta:
        app_label = 'polargraph'
