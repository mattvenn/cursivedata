from django.conf.urls import url

from . import views
from . import gcode

urlpatterns = [
    url(r'^upload_gcode', gcode.upload_gcode, name='upload_gcode'),
    #url(r'^$', views.index, name='index'),
]
