'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
from django.utils import timezone
from imp import find_module, load_module
import jsonfield
from cursivedata.models.drawing_state import StoredOutput, DrawingState
from django.utils.datetime_safe import datetime
from cursivedata.models.data import DataStore,  FakeDataStore
from cursivedata.drawing import Drawing


#Points to some code and associated parameters which are needed to process data
#This is not an actual running generator, but an template to make new real generators
class Generator( models.Model ) :
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000,default="Unknown")
    image = models.CharField(max_length=200,default="No Image")
    file_path = models.CharField(max_length=200,default="./generators")
    module_name = models.CharField(max_length=200,unique=True)
    #last_updated is actually creation date
    last_updated = models.DateTimeField("Last Updated",default=timezone.now())
    #last_used is when the generator was last used by a pipeline
    last_used = models.DateTimeField("Last Used",default=timezone.now())
    
    module = None
    def __init__(self, *args, **kwargs):
        super(Generator, self).__init__(*args, **kwargs)
        #put this in so that when we add parameters we'll have a valid id for them to use as a foreign key
        should_work = True
        if not self.id: 
            self.save()
            should_work = False
        try: #Its OK to for the module loading to not work if we haven't been saved
            self.module = self.get_file( self.module_name )
            for param in self.module.get_params():
                self.add_or_update_param( param )
        except Exception as e:
            if should_work :
                #raise e
                print "Empty module",e
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
    
    def get_filename(self):
        return self.file_path + "/" + self.module_name + ".py"
    
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

    def get_state( self, save=True) :
        s = GeneratorState( name=self.name, generator=self )
        if save :
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
    
    #Gets the current values for all parameters as a dict
    def get_param_dict(self,param_values):
        params = []
        for param in self.parameter_set.all():
            params.append({"name":param.name,
                           "description":param.description,
                           "value":param_values.get(param.name,param.default)})
        return params
    
    def get_recent_output(self,start=0,end=3):
        return StoredOutput.objects.order_by('-modified').filter(generator=self,status="complete",filetype="svg")[start:end]            

    #called by pipeline after an update
    def update_last_used(self):
        self.last_used = timezone.now()
        self.save();

    class Meta:
        app_label = 'cursivedata'
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.id)


#Generators have parameters. These can result in UI elements
class Parameter( models.Model ) :
    name = models.CharField(max_length=200)
    default = models.FloatField(default=0,blank=True)
    description = models.CharField(default="Some parameter",blank=True,max_length=1000)
    generator = models.ForeignKey( Generator )

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'cursivedata'

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
        app_label = 'cursivedata'

#Generator should be self explanatory
#ds_form is a SelectOrMakeDataStore
#ds_settings is a DataStoreSettings, which can give query params
#params is a Dict, with:
## param_<x> for params
from cStringIO import StringIO
import sys
class GeneratorRunner(DrawingState):        
    def run(self,generator,input_data,input_params,width,height):
        data = FakeDataStore()
        data.load_data(input_data)
        
        state = generator.get_state(False) 
        print "State:",state.state
        params = state.params
        for (key, value) in input_params.iteritems():
            params[key] = value
        internal = {}
        doc = self.create_svg_doc(width, height) #in mm
        drwg = Drawing( doc )
        #capture prints to stdout
        backup = sys.stdout
        sys.stdout = StringIO()
        #do the processing
        generator.begin_drawing( drwg, params, internal )
        generator.process_data(  drwg, data, params, internal )
        generator.end_drawing( drwg, params, internal )
        #grab the output
        out = sys.stdout.getvalue()
        output_lines = []
        #take opportunity to supress inkscape warnings...
        for line in out.splitlines():
            if not line.endswith("not found in:svg"):
                output_lines.append(line)
            
        #set the stdout back to normal
        sys.stdout.close()
        sys.stdout = backup
        fn = self.filename()
        doc.save(fn)
        return (fn,output_lines);
        
    
    def filename(self):
        return "data/working/tmp.svg"
