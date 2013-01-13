# Create your views here.

from django.http import HttpResponse, Http404
from polargraph.models import *
from django.shortcuts import render

def index(request):
    latest_pipelines = Pipeline.objects.order_by('-last_updated')[:5]
    output = ', '.join([p.name for p in latest_pipelines])
    return HttpResponse(output)


def show_pipeline(request, pipelineID):
    try:
        pipeline = Pipeline.objects.get(pk=pipelineID)
        context = {"pipeline":pipeline}
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
    


