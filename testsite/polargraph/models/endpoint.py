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
import requests



#A Robot, or other output device
class Endpoint( models.Model ):
    name = models.CharField(max_length=200)
    device = models.CharField(max_length=200)
    width = models.CharField(max_length=200)
    height = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    
    def add_svg(self,svg_file ):
        gcode_file = svg.get_temp_filename("gcode")
        svg.convert_svg_to_gcode(svg_file, gcode_file)
        self.send_to_device(gcode_file)
        
    def send_to_device(self,gcode):
        print "Seinding gcode file",gcode,"to",self.device,"at",self.location
        
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'polargraph'