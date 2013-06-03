from os.path import join

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
admin.autodiscover()

from polargraph import views
from polargraph.api import DataStoreResource, COSMSourceResource, EndpointResource

from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(DataStoreResource())
v1_api.register(COSMSourceResource())
v1_api.register(EndpointResource())

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
     url(r'^admin/', include(admin.site.urls)),

     
     url(r'^api/', include(v1_api.urls)), #e.g. /api/v1/datastore/?format=json
     
     (r'^data/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': join(settings.PROJECT_ROOT, 'data')}),
     (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': join(settings.PROJECT_ROOT, 'media')}),
     
     url(r'^login', 'django.contrib.auth.views.login', name="login"),
     url(r'^logout', 'django.contrib.auth.views.logout',
         {'next_page': reverse_lazy('polargraph:index')}, name='logout'),
#     url(r'^$', 'landing.views.landing', name='landing'),

     #url(r'^polargraph/', include('polargraph.urls',namespace='polargraph',app_name='polargraph')),
     url(r'^', include('polargraph.urls',namespace='polargraph',app_name='polargraph')),
)
