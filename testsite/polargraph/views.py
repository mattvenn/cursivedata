# Create your views here.

from django.http import HttpResponse, Http404
from polargraph.models import *
from django.shortcuts import render

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
        if act == "Update Parameters":
            for (key, value) in request.POST.iteritems():
                if key.startswith("param"):
                    pipeline.state.params[key.replace("param","")]= float(value)
            pipeline.state.save()
        elif act != "none":
            print "Unknown action:",act
        context = {"pipeline":pipeline, "params": pipeline.state.params }
        return render(request,"pipeline_display.html",context)
    except Pipeline.DoesNotExist:
        raise Http404
        
def update(request, pipelineID):
    try:
        pipeline = Pipeline.objects.get(pk=pipelineID)
        pipeline.generator.init()
    except Pipeline.DoesNotExist:
        raise Http404
    return HttpResponse(pipeline.update())
    


