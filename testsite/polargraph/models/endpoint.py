'''
Created on 12 Jan 2013

@author: dmrust
'''

from django.db import models
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
    
    def add_svg(self,svg_file, generator_params ):
        print "Adding SVG"
        so = GCodeOutput(endpoint=self)
        so.save()
        svg.convert_svg_to_gcode(self,generator_params,svg_file,so.get_filename())
        
    def get_next_filename(self):
        n = self.get_next()
        if n:
            return n.get_filename()
        return None
    
    def get_next(self):
        try:
            return GCodeOutput.objects.filter(endpoint=self,served=False).order_by('modified')[:1].get()
        except Exception as e:
            return None
        
    def consume(self):
        n = self.get_next( );
        n.served = True;
        n.save()
        
    def send_to_device(self,gcode):
        print "Sending gcode file",gcode,"to",self.device,"at",self.location
        
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'polargraph'

class GCodeOutput( models.Model ):
    endpoint = models.ForeignKey(Endpoint)
    served = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)
    
    def get_filename(self):
        if not self.id > 0:
            self.save()
        return "data/output/gcode/"+str(self.id)+".gcode"
    
    class Meta:
        app_label = 'polargraph'