from django.conf.urls import patterns, url
from django.views.generic.simple import direct_to_template

from polargraph import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),

	 # ex: /polargraph/pipeline/5/update/
    
    #Show pipelines
    url(r'^pipeline/?$', views.list_pipelines, name='list_pipelines'),
    url(r'^pipeline/embed/(?P<pipelineID>\d+)/$', views.embed_pipeline, name='embed_pipeline'),
    url(r'^pipeline/(?P<pipelineID>\d+)/$', views.show_pipeline, name='show_pipeline'),

    url(r'^sources/?$', views.list_sources, name='list_sources'),
    url(r'^sources/(?P<sourceID>\d+)/$', views.show_source, name='show_source'),
    url(r'^sources/create/?$', views.create_source, name='create_source'),
    
    #Do stuff to pipelines
    url(r'^pipeline/create/?$', views.create_pipeline, name='create_pipeline'),
    url(r'^pipeline/(?P<pipelineID>\d+)/update/$', views.update, name='update'),
    
    #Show endpoints
    url(r'^endpoint/?$', views.list_endpoints, name='list_endpoints'),
    url(r'^endpoint/create/?$', views.create_endpoint, name='create_endpoint'),
    url(r'^endpoint/(?P<endpointID>\d+)/$', views.show_endpoint, name='show_endpoint'),
    
    #Do stuff with endpoints
    url(r'^endpoint_data/(?P<endpointID>\d+)/$', views.get_gcode, name='get_gcode'),
    
    #Show generators
    url(r'^generator/?$', views.list_generators, name='list_generators'),
    url(r'^generator/create/?$', views.create_generator, name='create_generator'),
    url(r'^generator/(?P<generatorID>\d+)/$', views.show_generator, name='show_generator'),

    url(r'^contact',  views.contact, name='contact'),
    url(r'^contact/thankyou', direct_to_template, {'template': 'thankyou.html'}, name="thankyou"),
)

