from os.path import join

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
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
    (r'^data/(?P<path>.*)$', 'django.views.static.serve', {'document_root': join(settings.PROJECT_ROOT, 'data')}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': join(settings.PROJECT_ROOT, 'media')}),

    url(r'^login', 'django.contrib.auth.views.login', name="login"),
    url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': reverse_lazy('polargraph:index')}, name='logout'),

    url(r'^about', direct_to_template, {'template': 'about.html'}, name="about"),
    url(r'^people', direct_to_template, {'template': 'people.html'}, name="people"),
    url(r'^license', direct_to_template, {'template': 'license.html'}, name="license"),
    url(r'^getarobot', direct_to_template, {'template': 'getarobot.html'}, name="getarobot"),

    #the polargraph app's urls
    url(r'^', include('polargraph.urls',namespace='polargraph',app_name='polargraph')),
)
