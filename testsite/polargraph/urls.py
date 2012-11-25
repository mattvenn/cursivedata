from django.conf.urls import patterns, url

from polargraph import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),

	 # ex: /polargraph/5/update/
    url(r'^(?P<pipelineID>\d+)/update/$', views.update, name='update'),
)

