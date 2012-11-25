# Create your views here.

from django.http import HttpResponse
from polargraph.models import *

def index(request):
	latest_pipelines = Pipeline.objects.order_by('-lastUpdated')[:5]
	output = ', '.join([p.name for p in latest_pipelines])
	return HttpResponse(output)


def update(request, pipelineID):
	try:
		pipeline = Pipeline.objects.get(pk=pipelineID)
		pipeline.generator.init()
	except Pipeline.DoesNotExist:
		raise Http404
	return HttpResponse(pipeline.update())
	


