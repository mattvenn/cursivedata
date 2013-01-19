# Create your views here.

from django.http import HttpResponse, Http404
from django.core.servers.basehttp import FileWrapper
from polargraph.models import *
from django.shortcuts import render
import os


def index(request):
    latest_pipelines = Pipeline.objects.order_by('-last_updated')[:50]
    context = {"pipeline_list":latest_pipelines}
    return render(request,"pipeline_list.html",context)


def show_pipeline(request, pipelineID):
    try:
        pipeline = Pipeline.objects.get(pk=pipelineID)
        act = request.POST.get('action',"none")
        if act == "Reset":
            pipeline.reset()
        elif act == "Update Parameters":
            for (key, value) in request.POST.iteritems():
                if key.startswith("param"):
                    pipeline.state.params[key.replace("param","")]= float(value)
            pipeline.state.save()
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
        context = {"pipeline":pipeline, "params":params, "output":outputs }
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
    

