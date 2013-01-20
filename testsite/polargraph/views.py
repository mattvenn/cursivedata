# Create your views here.

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
from polargraph.models import *
from django.shortcuts import render
import os
from django.forms.models import ModelForm
from django.forms.widgets import Textarea, TextInput
from django.utils.datetime_safe import datetime
import re


def index(request):
    latest_pipelines = Pipeline.objects.order_by('-last_updated')[:50]
    context = {"pipeline_list":latest_pipelines}
    return render(request,"pipeline_list.html",context)


def show_pipeline(request, pipelineID):
    try:
        if request.method == 'POST': # If the form has been submitted...
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
        act = request.POST.get('action',"none")
        if act == "Reset":
            pipeline.reset()
        elif act == "Update Size":
            pipeline.img_width = int(request.POST.get('pipeWidth',pipeline.img_width))
            pipeline.img_height = int(request.POST.get('pipeHeight',pipeline.img_height))
            pipeline.reset()
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
        
        
        
        params = []
        for param in pipeline.generator.parameter_set.all():
            params.append({"name":param.name,
                           "description":param.description,
                           "value":pipeline.state.params.get(param.name,param.default)})
        outputs = StoredOutput.objects \
                .order_by('-modified') \
                .filter(pipeline=pipeline,status="complete",filetype="svg") \
                .exclude(run_id= pipeline.run_id)[:8]
        cosm_triggers = COSMSource.objects \
                .filter(data_store=pipeline.data_store)
        context = {"pipeline":pipeline, "params":params, "output":outputs, "cosm_form":cosm_form, "cosm_triggers":cosm_triggers }
        return render(request,"pipeline_display.html",context)
    except Pipeline.DoesNotExist:
        raise Http404

def show_endpoint(request, endpointID):
    try:
        endpoint = Endpoint.objects.get(pk=endpointID)
        act = request.POST.get('action',"none")
        if act == "Calibrate":
            print "Calibrating..."
        elif act == "Update Parameters":
            print "Update Params"
        elif act != "none":
            print "Unknown action:",act
        previous = StoredOutput.objects \
                .order_by('-modified') \
                .filter(endpoint=endpoint,status="complete",filetype="svg")[1:8] 
        current_full = StoredOutput.objects \
                .order_by('-modified') \
                .filter(endpoint=endpoint,status="complete",filetype="svg")[0]
        current_update = StoredOutput.objects \
                .order_by('-modified') \
                .filter(endpoint=endpoint,status="partial",filetype="svg")[0]
        context = {"endpoint":endpoint, "previous":previous, "current_full":current_full, "current_update":current_update}
        return render(request,"endpoint_display.html",context)
    except Endpoint.DoesNotExist:
        raise Http404
    
def get_gcode(request, endpointID ):
    endpoint = Endpoint.objects.get(pk=endpointID)
    filename = endpoint.get_next_filename()
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
        pipeline.generator.init()
    except Pipeline.DoesNotExist:
        raise Http404
    return HttpResponse(pipeline.update())
    
def create_pipeline( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = PipelineCreation(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            pipeline = form.save(commit=False);
            ds = DataStore(name="Data for"+str(pipeline.name))
            gs = GeneratorState(name="Data for"+str(pipeline.name), generator=pipeline.generator)
            ds.save()
            gs.save()
            pipeline.data_store = ds
            pipeline.state = gs
            pipeline.last_updated = datetime.now()
            pipeline.save()
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
        fields = ( 'cosm_url', 'feed_id', 'stream_id', 'api_key', 'url_base')