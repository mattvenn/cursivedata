from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

    url(r'^', include('roboserver.urls',namespace='roboserver',app_name='roboserver')),
    #url(r'^admin/', include(admin.site.urls)),

    # url(r'^$', 'pi_server.views.home', name='home'),
    # url(r'^pi_server/', include('pi_server.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
