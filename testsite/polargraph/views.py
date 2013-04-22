# Create your views here.

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
from polargraph.models import *
from polargraph.models.generator import GeneratorRunner
from django.shortcuts import render
import os
import shutil
from django.forms.models import ModelForm
from django.forms.widgets import Textarea, TextInput
from django.utils.datetime_safe import datetime
from django import forms
import re

def index(request):
    latest_pipelines = Pipeline.objects.order_by('-last_updated')[:3]
    generators = Generator.objects.count()
    endpoints = Endpoint.objects.count()
    context = {"latest_pipelines":latest_pipelines, "generators" : generators, "endpoints" : endpoints}
    return render(request,"index.html",context)

def list_sources(request):
    latest_sources = COSMSource.objects.order_by('-last_updated')[:50]
    context = {"source_list":latest_sources}
    return render(request,"sources_list.html",context)

def list_pipelines(request):
    latest_pipelines = Pipeline.objects.order_by('-last_updated')[:50]
    context = {"pipeline_list":latest_pipelines}
    return render(request,"pipeline_list.html",context)

def list_endpoints(request):
    latest_endpoints = Endpoint.objects.order_by('-last_updated')[:50]
    context = {"endpoint_list":latest_endpoints}
    return render(request,"endpoint_list.html",context)

def list_generators(request):
    latest_generators = Generator.objects.order_by('-last_used')[:50]
    context = {"generator_list":latest_generators}
    return render(request,"generator_list.html",context)



def create_source(request):
    if request.method == 'POST': # If the form has been submitted...
        form = COSMSourceCreation(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            source = form.save(commit=False);
            #what is the right way to do this?
            ds = DataStore(name="Data for feed id " + str(source.feed_id))
            ds.save()
            source.data_store_id = ds.id
            source.save()
            return HttpResponseRedirect('/polargraph/sources/'+str(source.id)+"/") # Redirect after POST
    else:
        form = COSMSourceCreation() # An unbound form

    return render(request, 'source_create.html', {
        'form': form,
    })
    """
    try:
        act = request.POST.get('action',"none")
        if request.method == 'POST' and act == "Create COSM": # If the form has been submitted...
            cosm_form = COSMSourceCreation(request.POST) # A form bound to the POST data
        else:
            cosm_form = COSMSourceCreation( {
                    'url_base':request.get_host(),
                    'cosm_url':"http://api.cosm.com/v2/triggers/",
                    'stream_id':"1",
                    'feed_id':"96779",
                    'api_key':"WsH6oBOmVbflt5ytsSYHYVGQzCaSAKw0Ti92WHZzajZHWT0g",
                    }) # An unbound form
        
        if act == "Create COSM" and cosm_form.is_valid():
            if cosm_form.is_valid(): # All validation rules pass
                cosm_source = cosm_form.save(commit=False);
                cosm_source.data_store=pipeline.data_store
                cosm_source.save()

        context = {"source":cosm_source, "cosm_form":cosm_form}
        return render(request,"source_create.html",context)
    except COSMSource.DoesNotExist:
        raise Http404
        """
"""
    if request.method == 'POST': # If the form has been submitted...
        form = PipelineCreation(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            pipeline = form.save(commit=False);
            pipeline.init_data();
            return HttpResponseRedirect('/polargraph/pipeline/'+str(pipeline.id)+"/") # Redirect after POST
    else:
        form = PipelineCreation() # An unbound form

    return render(request, 'pipeline_create.html', { 'form': form,
"""

def show_pipeline(request, pipelineID):
    try:
        act = request.POST.get('action',"none")
        
        pipeline = Pipeline.objects.get(pk=pipelineID)
        if act == "Reset":
            pipeline.reset()
        if act == "Modify":
            form = PipelineModify(request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                #better way of doing this?
                pipeline.data_store = form.cleaned_data['data_store']
                pipeline.generator = form.cleaned_data['generator']
                pipeline.endpoint = form.cleaned_data['endpoint']
                pipeline.save()
        elif act == "Begin":
            pipeline.begin()
        elif act == "End":
            pipeline.end()
        elif act == "Auto Size":
            pipeline.print_top_left_x = 0
            pipeline.print_top_left_y = 0
            pipeline.print_width = pipeline.endpoint.img_width
            print pipeline.print_width
            pipeline.update_size(pipeline.endpoint.img_width,pipeline.endpoint.img_height)
            pipeline.save()
        elif act == "Update Size":
            pipeline.update_size( int(request.POST.get('pipeWidth',pipeline.img_width)),
                    int(request.POST.get('pipeHeight',pipeline.img_height)))
        elif act == "Update Print Location":
            pipeline.print_top_left_x = request.POST.get("xOffset")
            pipeline.print_top_left_y = request.POST.get("yOffset")
            pipeline.print_width = request.POST.get("printWidth")
            pipeline.save()
        elif act == "Update Parameters":
            for (key, value) in request.POST.iteritems():
                if key.startswith("param"):
                    pipeline.state.params[key.replace("param","")]= float(value)
            pipeline.state.save()
        elif act != "none":
            print "Unknown action:",act
        
        form = PipelineModify(instance=pipeline) # An unbound form
        context = {"pipeline":pipeline, "form": form}
        return render(request,"pipeline_display.html",context)
    except Pipeline.DoesNotExist:
        raise Http404
    
def show_source(request,sourceID):
    try:
        act = request.POST.get('action',"none")

        cs = COSMSource.objects.get(id=sourceID)
        if act == "Enable" :
            if not cs.is_running():
                cs.start_trigger()
        if act == "Disable" :
            if cs.is_running():
                cs.stop_trigger()
        if act == "Delete" :
            if cs.is_running():
                cs.stop_trigger()
            cs.delete()
            return HttpResponseRedirect('/polargraph/sources') # Redirect after delete

        context = {"source":cs}
        return render(request,"source_display.html",context)
    except COSMSource.DoesNotExist:
        raise Http404

def show_endpoint(request, endpointID):
    try:
        endpoint = Endpoint.objects.get(pk=endpointID)
        act = request.POST.get('action',"none")
        if act == "Calibrate":
            print "Calibrating..."
            endpoint.calibrate()
        elif act == "Reset":
            print endpoint.reset()
        elif act == "Resume":
            print "resume"
            endpoint.resume()
        elif act == "Pause":
            print "pause"
            print endpoint.pause()
        elif act == "Update Parameters":
            print "Update Params"
        elif act != "none":
            print "Unknown action:",act
        previous = endpoint.get_recent_output()
        files_left = endpoint.get_num_files_to_serve()
        context = {"endpoint":endpoint, "previous":previous,"files_left":files_left}
        return render(request,"endpoint_display.html",context)
    except Endpoint.DoesNotExist:
        raise Http404

def create_generator(request):
    create_form = GeneratorSource()
    create_message = None;
    if request.POST:
        create_form = GeneratorSource(request.POST,request.FILES)
        if create_form.is_valid() :
            source_id=create_form.cleaned_data['source_id']
            name=create_form.cleaned_data['name']
            description=create_form.cleaned_data['description']
            module_name=create_form.cleaned_data['module_name']
            
            source = create_form.cleaned_data['source_id']
            print "Source:",source
            g = Generator( name=name, description=description, module_name=module_name )
            shutil.copy(source.get_filename(), g.get_filename())
            g.save()
            return HttpResponseRedirect('/polargraph/generator/'+str(g.id)+"/") # Redirect after POST
    context = {"create":create_form}
    r = render(request,"generator_create.html",context)
    return r;
        
    
class GeneratorSource(forms.Form):
    source_id = forms.ModelChoiceField(queryset=Generator.objects.all(),label="Base this generator on another one")
    source_file  = forms.FileField(label="Upload new file (not implemented yet)",required=False)
    name = forms.CharField(label="Name",initial="New Generator")
    description = forms.CharField(label="Describe your generator",initial="This generator does .... ",
                           widget = forms.widgets.Textarea(attrs={'cols': 80, 'rows': 1}) )
    module_name = forms.CharField(label="Choose a unique filename",initial="filename")
    
    def clean_module_name(self):
        data = self.cleaned_data['module_name']
        if Generator.objects.filter(module_name=data).count() > 0 :
            raise forms.ValidationError("Module name already exists: " + data )
        p = re.compile('^[a-zA-Z_]+$')
        if not p.match(data):
            raise forms.ValidationError("Filename can only have letters and underscores. You had: " + data )
        return data
    
        
def show_generator(request, generatorID):
    try:
        generator = Generator.objects.get(pk=generatorID)
        #Create forms to use
        if request.POST:
            ds_form = SelectOrMakeDataStore(request.POST,request.FILES)
            select_form = DataStoreSettings(request.POST)
        else:
            ds_form = SelectOrMakeDataStore()
            select_form = DataStoreSettings()
            
        ds_form.get_data_store()
                
        #Setup width and height
        width = int(request.POST.get("width","400"))
        height = int(request.POST.get("height","400"))
        
        #Get parameter values
        param_values = {}
        for (key, value) in request.POST.iteritems():
            if key.startswith("param"):
                param_values[key.replace("param","")]= float(value)
        params = generator.get_param_dict(param_values)
        
        filename = None
        
        data = select_form.query_data_store(ds_form.data_store)
        print "loaded %d lines" % len(data)
        
        act = request.POST.get('action',"none")
        if act == "Run" :
            if ds_form.data_store :
                filename = GeneratorRunner().run(generator,data,param_values,width,height)
            else:
                print "No data store setup"
        elif act == "Create Datastore":
            ds_form.create_data_store(request.POST.get("ds_name","Unnamed Datastore"))
        elif act == "Import CSV":
            ds_form.load_csv(request.FILES['csv_file'], "Time")
        elif act == "Update Query":
            ds_form.load_csv(request.FILES['csv_file'], "Time")
        elif act == "Save Code":
            code_form = GeneratorCode(request.POST)
            code_form.save_code(generator)
        else:
            print "Unknown Action:",act
            
        code_form = GeneratorCode()
        code_form.load_code(generator)
        
        context = {"generator":generator,"output":filename, "data_store":ds_form.data_store, 
                    "width":width, "height":height, "params":params, "data": data,
                    "ds_form":ds_form, "select_form":select_form, "code_form":code_form }
        return render(request,"generator_display.html",context)
    except Generator.DoesNotExist:
        raise Http404

class SelectOrMakeDataStore(forms.Form):
    data_store_id = forms.ModelChoiceField(queryset=DataStore.objects.all(),label="Select")
    csv_file  = forms.FileField(label="Load CSV Data - needs a header with Time,value",required=False)
    ds_name = forms.CharField(label="New DS Name",initial="New Datastore")
    data_store = None
    
    def get_data_store(self):
        if self.is_valid() :
            self.data_store = self.cleaned_data['data_store_id']
    def create_data_store(self,name):
        self.data_store = DataStore(name=request.POST.get("ds_name","Unnamed Datastore"))
        self.data_store.save()
    def load_csv(self,file,time_field):
        if self.data_store :
            self.data_store.load_from_csv(file.read().split("\n"),time_field=time_field)
        else:
            print "generator doesn't have a data store yet"
    
class DataStoreSettings(forms.Form):
    max_time = forms.DateTimeField(label="Data Before",required=False)
    min_time = forms.DateTimeField(label="Data After",required=False)
    max_records = forms.IntegerField(label="Limit records to",required=False)
    def get_params(self):
        return { "max_date": self.max_date, 
                "min_date":self.min_date, "max_records":self.max_records}
    def query_data_store(self,data_store):
        if not data_store:
            return []
        if self.is_valid( ):
	        return data_store.query(max_time=self.cleaned_data['max_time'],
                                    min_time=self.cleaned_data['min_time'],
                                    max_records=self.cleaned_data['max_records'])
        return data_store.query()

class GeneratorCode(forms.Form):
    code_field = forms.CharField(label="Codez",widget = forms.widgets.Textarea(attrs={'cols': 80, 'rows': 50}))
    def load_code(self,generator):
        with open(generator.get_filename(), 'rb') as codefile:
	        self.fields['code_field'].initial = codefile.read()
    def save_code(self,generator):
        if self.is_valid():
            with open(generator.get_filename(), 'wb') as codefile:
                codefile.write(self.cleaned_data['code_field'])
                codefile.close()
    
def get_gcode(request, endpointID ):
    try:
        endpoint = Endpoint.objects.get(pk=endpointID)
        filename = endpoint.get_next_filename()
    except Endpoint.DoesNotExist:
        raise Http404
    if endpoint.paused:
        print "endpoint is paused"
        raise Http404
    print "Filename",filename
    if not filename:
        raise Http404
    consume =request.REQUEST.get('consume',False)
    if consume:
        print "Consuming..."
        endpoint.consume()
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response
        
        
def update(request, pipelineID):
    try:
        pipeline = Pipeline.objects.get(pk=pipelineID)
    except Pipeline.DoesNotExist:
        raise Http404
    return HttpResponse(pipeline.update())
    
def create_endpoint( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = EndpointCreation(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            endpoint = form.save(commit=False);
            endpoint.save()
            return HttpResponseRedirect('/polargraph/endpoint/'+str(endpoint.id)+"/") # Redirect after POST
    else:
        form = EndpointCreation() # An unbound form

    return render(request, 'endpoint_create.html', {
        'form': form,
    })

def create_pipeline( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = PipelineCreation(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            pipeline = form.save(commit=False);
            pipeline.init_data();
            return HttpResponseRedirect('/polargraph/pipeline/'+str(pipeline.id)+"/") # Redirect after POST
    else:
        form = PipelineCreation() # An unbound form

    return render(request, 'pipeline_create.html', {
        'form': form,
    })



class EndpointCreation(ModelForm):
    class Meta:
        model = Endpoint
        fields = ( 'name', 'device', 'location' )
        

class PipelineModify(ModelForm):
    class Meta:
        model = Pipeline
        fields = ( 'data_store', 'generator', 'endpoint' )

class PipelineCreation(ModelForm):
    class Meta:
        model = Pipeline
        fields = ( 'name', 'description', 'data_store', 'generator', 'endpoint', 'img_width', 'img_height' )
        widgets = {
            'description': Textarea(attrs={'cols': 60, 'rows': 1}),
            'name': TextInput(attrs={'size': 60}),
        }

class COSMSourceCreation(ModelForm):
    class Meta:
        model = COSMSource
        #fields = ( 'cosm_url', 'feed_id', 'stream_id', 'api_key', 'url_base', 'add_location', 'use_stream_id', 'add_feed_title', 'add_feed_id')
        fields = ( 'feed_id', 'stream_id' )
