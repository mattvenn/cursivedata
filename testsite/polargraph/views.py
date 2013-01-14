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
        
def update(request, pipelineID):
    try:
        pipeline = Pipeline.objects.get(pk=pipelineID)
        pipeline.generator.init()
    except Pipeline.DoesNotExist:
        raise Http404
    return HttpResponse(pipeline.update())
    


