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
        self.module = get_file( self.module_name )
        return
    #Processes a given chunk of data to return some SVG
    def process_data( self, data, state ) :
        #print "Processing data with",map(str,state.generatorstateparameter_set.all())
        return self.module.process(data,state)
    def __unicode__(self):
        return self.name
    @staticmethod
    def create_from_file(module_name) :
        mod = Generator.get_file( module_name )
        g = Generator( name=mod.get_name(), description=mod.get_description(), module_name=module_name )
        g.save();
        for p in mod.get_params() :
            param = Parameter( name=p["name"] )
            g.parameter_set.add( param )
            param.save()
        return g;
            
    @staticmethod
    def get_file(module_name) : #No error checking yet!
        f, filename, data = find_module(module_name, ["./scripts"])
        return load_module(module_name, f, filename, data)

class Parameter( models.Model ) :
    name = models.CharField(max_length=200)
    generator = models.ForeignKey( Generator )
    def __unicode__(self):
        return self.name
        

class DataSource( models.Model ) :
    name = models.CharField(max_length=200)
    #Returns the next bit of data to be drawn
    def getNextData(self) : 
        return ""
    def __unicode__(self):
        return self.name

class GeneratorState( models.Model ):
    name = models.CharField(max_length=200)
    generator = models.ForeignKey( Generator )
    def __unicode__(self):
        return self.name

class GeneratorStateParameter( models.Model ):
    parameter = models.ForeignKey( Parameter )
    state = models.ForeignKey( GeneratorState )
    value = models.FloatField()
    def __unicode__(self):
        return self.parameter.name+"="+str(self.value)

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
        data = self.data_source.getNextData()
        print "Data",str(data)
        state = self.state 
        print "State",str(state)
        retVal = self.generator.process_data( data, state )
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
