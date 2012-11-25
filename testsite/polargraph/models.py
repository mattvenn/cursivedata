from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from imp import find_module, load_module

# Create your models here.


#Points to some code and associated parameters which are needed to process data
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
    def process_data( self, data, params, state ) :
        #print "Processing data with",map(str,state.generatorstateparameter_set.all())
        return self.module.process(data,params,state)
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

class Parameter( models.Model ) :
    name = models.CharField(max_length=200)
    default = models.FloatField()
    generator = models.ForeignKey( Generator )
    def __unicode__(self):
        return self.name
        

class DataSource( models.Model ) :
    name = models.CharField(max_length=200)
    #Returns the next bit of data to be drawn
    def get_next_data(self) : 
        return ""
    def __unicode__(self):
        return self.name

#Testing data source which just reads a file in
class FileDataSource( DataSource ) :
    def __init__( self, file_name ):
        self.file_name = file_name
    file_name = "example.csv";
    def get_next_data(self) :
        data = [];
        f = open(self.file_name, 'r')
        for line in f :
            l = line.strip();
            if len(l) > 0 :
                time,sep,val = l.partition(",")
                d = (float(time),float(val))
                data.append(d )
        return data

    

class GeneratorState( models.Model ):
    name = models.CharField(max_length=200)
    generator = models.ForeignKey( Generator )
    params = {}
    def update(self) :
        for p in self.generatorstateparameter_set:
            self.params[p.parameter.name] = p
        
    def get_param(self,name) :
        self.update() #Ugly - find a better way when Dave understands the database model better
        return self.params[name].value
    def __unicode__(self):
        return self.name

    def params_to_dict(self) :
        state = {}
        for p in self.generatorstateparameter_set.all():
            state[p.parameter.name] = p.value
        return state
    def params_from_dict(self,data):
        self.update()
        for (key,value) in data.iteritems() :
            self.params[key].value = value


class GeneratorStateParameter( models.Model ):
    parameter = models.ForeignKey( Parameter )
    state = models.ForeignKey( GeneratorState )
    value = models.FloatField()
    def __unicode__(self):
        return self.parameter.name+"="+str(self.value)

#A Robot, or other output device
class Endpoint( models.Model ):
    name = models.CharField(max_length=200)
    device = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name

#A complete pipeline from data source through to a running algorithm
class Pipeline( models.Model ) :
    name = models.CharField(max_length=200)
    generator = models.ForeignKey( Generator )
    data_source = models.ForeignKey( DataSource )
    state = models.ForeignKey( GeneratorState )
    endpoint = models.ForeignKey( Endpoint )
    current_image = models.CharField(max_length=200)
    last_updated = models.DateTimeField("Last Updated")
    def __unicode__(self):
        return self.name

    #Executes the pipeline by running the generator on the next bit of data
    def update( self ) :
        data = self.data_source.get_next_data()
        params = self.state.params_to_dict();
        retVal = self.generator.process_data( data, params, state )
        self.state.save()
        print str(self),"using",str(self.generator),"to send to endpoint", str(self.endpoint)
        print "Sending data", str( retVal  )
        return retVal;

def setup_test_data() :
    su = User.objects.all()[0]
    su.set_password('admin')
    su.save()
    g1 = Generator(name="Test Generator", description="This is a fake generator to test stuff with", image="No Image", module_name="example")
    g1.save()
    g1p = Parameter(name="Param 1",generator=g1)
    g1p.save()
    g1s = GeneratorState(name="Current",generator=g1)
    g1s.save()
    g1p1s = GeneratorStateParameter(state=g1s,parameter=g1p,value=7)
    g1p1s.save()
    e1 = Endpoint(name="My Robot",device="Polargraph",location="Under the stairs" )
    e1.save()
    d1 = DataSource()
    d1.save()
    p1 = Pipeline(name="Test Pipeline",data_source=d1, generator=g1, endpoint=e1,state=g1s, last_updated=timezone.now() )
    p1.save()
    return p1

def testing() :
    g = Generator.create_from_file("squares2")
    g.save()
    gs = g.get_state()
    g.init()
    data = [ (0,1), (1,2), (3,4) ]
    state = { "number":2, "startenv":1 }
    g.process_data( data, gs.params_to_dict(), state )
