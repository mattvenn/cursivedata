# Create your views here.

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
from polargraph.models import *
from polargraph.models.generator import GeneratorRunner
from django.shortcuts import render
import os
from django.forms.models import ModelForm
from django.forms.widgets import Textarea, TextInput
from django.utils.datetime_safe import datetime
from django import forms
import re

def index(request):
    latest_pipelines = Pipeline.objects.order_by('-last_updated')[:50]
    context = {"pipeline_list":latest_pipelines}
    return render(request,"index.html",context)

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



def show_pipeline(request, pipelineID):
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
        
        pipeline = Pipeline.objects.get(pk=pipelineID)
        if act == "Reset":
            pipeline.reset()
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
        elif act == "Create COSM" and cosm_form.is_valid():
            if cosm_form.is_valid(): # All validation rules pass
                cosm_source = cosm_form.save(commit=False);
                cosm_source.data_store=pipeline.data_store
                cosm_source.save()
        elif re.match("^COSM.*", act) :
            m = re.match("COSM (\w+) (\d+)", act)
            cos_act = m.group(1)
            cos_id = m.group(2)
            cs = COSMSource.objects.get(id=cos_id)
            if cos_act == "Enable" :
                if not cs.is_running():
                    cs.start_trigger()
            if cos_act == "Disable" :
                if cs.is_running():
                    cs.stop_trigger()
            if cos_act == "Delete" :
                if cs.is_running():
                    cs.stop_trigger()
                cs.delete()
        elif act != "none":
            print "Unknown action:",act
        
        context = {"pipeline":pipeline, "cosm_form":cosm_form}
        return render(request,"pipeline_display.html",context)
    except Pipeline.DoesNotExist:
        raise Http404
    

def show_endpoint(request, endpointID):
    try:
        endpoint = Endpoint.objects.get(pk=endpointID)
        act = request.POST.get('action',"none")
        if act == "Calibrate":
            print "Calibrating..."
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
    
def show_generator(request, generatorID):
    try:
        generator = Generator.objects.get(pk=generatorID)
        act = request.POST.get('action',"none")
        
        filename = None
        data_store = None
        width = int(request.POST.get("width","400"))
        height = int(request.POST.get("height","400"))
        param_values = {}
        #Create forms to use
        if request.POST:
            ds_form = SelectOrMakeDataStore(request.POST,request.FILES)
            select_form = DataStoreSettings(request.POST)
            code_form = GeneratorCode(request.POST)
        else:
            ds_form = SelectOrMakeDataStore()
            select_form = DataStoreSettings()
            code_form = GeneratorCode()
            
        #Extract values from them
        if ds_form.is_valid():
            data_store = ds_form.cleaned_data['data_store']
            
        #Get other values by hand
        for (key, value) in request.POST.iteritems():
            if key.startswith("param"):
                param_values[key.replace("param","")]= float(value)
        params = generator.get_param_dict(param_values)
        
        if act == "Run" :
            if data_store :
                filename = GeneratorRunner().run(generator,data_store,param_values,width,height)
                print "Got filename",filename
            else:
                print "No data_store setup"
        elif act == "Create Datastore":
            data_store = DataStore(name=request.POST.get("ds_name","Unnamed Datastore"))
            data_store.save()
        elif act == "Import CSV":
            if data_store :
                file = request.FILES['csv_file'].read().split("\n")
                print "File:",file
                data_store.load_from_csv(file,time_field="Time")
        elif act == "Save Code":
            if code_form.is_valid():
                with open(generator.get_filename(), 'wb') as codefile:
                    codefile.write(code_form.cleaned_data['code_field'])
                    codefile.close()
        else:
            print "Unknown Action:",act
            
        with open(generator.get_filename(), 'rb') as codefile:
	        code_form.fields['code_field'].initial = codefile.read()
        
        context = {"generator":generator,"output":filename, "data_store":data_store, 
                    "width":width, "height":height, "params":params, 
                    "ds_form":ds_form, "select_form":select_form, "code_form":code_form }
        return render(request,"generator_display.html",context)
    except Generator.DoesNotExist:
        raise Http404

class SelectOrMakeDataStore(forms.Form):
    data_store = forms.ModelChoiceField(queryset=DataStore.objects.all(),label="Select",required=False)
    csv_file  = forms.FileField(label="Load CSV Data into current datastore",required=False)
    ds_name = forms.CharField(label="New DS Name",initial="New Datastore")
    
class DataStoreSettings(forms.Form):
    max_date = forms.DateTimeField(label="Data Before")
    min_date = forms.DateTimeField(label="Data After")
    max_records = forms.IntegerField(label="Limit records to")

class GeneratorCode(forms.Form):
    code_field = forms.CharField(label="Codez",widget = forms.widgets.Textarea(attrs={'cols': 80, 'rows': 20}))
    
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



class PipelineCreation(ModelForm):
    class Meta:
        model = Pipeline
        fields = ( 'name', 'description', 'generator', 'endpoint', 'img_width', 'img_height' )
        widgets = {
            'description': Textarea(attrs={'cols': 60, 'rows': 10}),
            'name': TextInput(attrs={'size': 60}),
        }

class COSMSourceCreation(ModelForm):
    class Meta:
        model = COSMSource
        fields = ( 'cosm_url', 'feed_id', 'stream_id', 'api_key', 'url_base', 'add_location', 'use_stream_id', 'add_feed_title', 'add_feed_id')
