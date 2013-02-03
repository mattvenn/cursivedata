from django.conf.urls import patterns, url

from polargraph import views

urlpatterns = patterns('',
    url(r'^$', views.list_pipelines, name='index'),

	 # ex: /polargraph/pipeline/5/update/
    
    #Show pipelines
    url(r'^pipeline/?$', views.list_pipelines, name='list_pipelines'),
    url(r'^pipeline/(?P<pipelineID>\d+)/$', views.show_pipeline, name='show_pipeline'),
    
    #Do stuff to pipelines
    url(r'^pipeline/create/?$', views.create_pipeline, name='create_pipeline'),
    url(r'^pipeline/(?P<pipelineID>\d+)/update/$', views.update, name='update'),
    
    #Show endpoints
    url(r'^endpoint/?$', views.list_endpoints, name='list_endpoints'),
    url(r'^endpoint/(?P<endpointID>\d+)/$', views.show_endpoint, name='show_endpoint'),
    
    #Do stuff with endpoints
    url(r'^endpoint_data/(?P<endpointID>\d+)/$', views.get_gcode, name='get_gcode'),
    
    #Show generators
    url(r'^generator/?$', views.list_generators, name='list_generators'),
    url(r'^generator/(?P<endpointID>\d+)/$', views.show_generator, name='show_generator'),
)

