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


#This takes in data that's been produced by some process and a) makes current stuff
#available, and b) stores historic values
#Has a flag to say if there's new data to be used
class DataStore( models.Model ) :
    name = models.CharField(max_length=200)
    current_data = models.CharField(max_length=20000,default=json.dumps([]))
    data_file = "tmp/data_store.json"
    available = models.BooleanField(default=False)
    fresh=False
    
    #After the data's been used, add it to the history and clear the current data
    def clear_current(self) : 
        current = json.loads(self.current_data)
        try:
            with open(self.data_file, 'rb') as hist_file:
                hist = json.load(hist_file)
        except Exception as e:
            print "Couldn't open history file: ", e
            hist = []
        try:
            with open(self.data_file, 'wb') as hist_file:
                json.dump(hist+current, hist_file)
        except Exception as e:
            print "Couldn't save history",e
        self.current_data = json.dumps([])
        self.available=False
        self.fresh=False
        self.save()
        
    #Returns the current next bit of data to be drawn
    def get_current(self) : 
        current = json.loads(self.current_data)
        return current
    
    #Adds the data to the current data and sets available to true
    #Data should be a list of dicts or lists - not sure which yet.
    def add_data(self,data):
        self.available=True
        self.fresh=True
        cur = self.get_current()
        total = cur + data
        totals = json.dumps(total)
        self.current_data = totals
        self.save()
        self.pipeline.update()
        
    def mark_stale(self):
        self.fresh=False
        self.save()
    
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'polargraph'