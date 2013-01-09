from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from polargraph import views
from polargraph.api import DataStoreResource, COSMEndpointResource

from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(DataStoreResource())
v1_api.register(COSMEndpointResource())

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'testsite.views.home', name='home'),
    # url(r'^testsite/', include('testsite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
     url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),

     url(r'^polargraph/', include('polargraph.urls')),
     
     url(r'^api/', include(v1_api.urls)), #e.g. /api/v1/datastore/?format=json
     
)
