'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from imp import find_module, load_module
import json
import csv
import polargraph.svg as svg
from polargraph.models.pipeline import StoredOutput
import requests



#A Robot, or other output device
class Endpoint( models.Model ):
    name = models.CharField(max_length=200)
    device = models.CharField(max_length=200)
    width = models.FloatField(max_length=200)
    side_margin = models.FloatField(max_length=200)
    top_margin = models.FloatField(max_length=200)
    height = models.FloatField(max_length=200)
    url = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    

    #dave fix
    def get_gcode_filename(self):
        return "/tmp/test.polar"

    def add_svg(self,svg_file,generator_params):
        filename = self.get_gcode_filename()
        svg.convert_svg_to_gcode(self,generator_params,svg_file,filename)
    
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'polargraph'
