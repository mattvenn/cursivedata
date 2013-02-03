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
import dateutil.parser
from copy import copy,deepcopy


#This takes in data that's been produced by some process and a) makes current stuff
#available, and b) stores historic values
#Has a flag to say if there's new data to be used
# Data format is a list of dicts. Each dict has a time field, containing the time it was created.
# When data is added, if it doesn't have a time, the current time is used
# When you get the data, all the time fields will be datetime objects
class DataStore( models.Model ) :
    name = models.CharField(max_length=200)
    current_data = models.CharField(max_length=20000,default=json.dumps([]))
    current = None
    historic_data = models.CharField(max_length=200000,default=json.dumps([]))
    available = models.BooleanField(default=False)
    fresh=False
    
    #After the data's been used, add it to the history and clear the current data
    def clear_current(self) : 
        current = json.loads(self.current_data)
        try:
            hist = json.loads(self.historic_data)
        except Exception as e:
            print "Couldn't load history:", e
            hist = []
        try:
            self.historic_data=json.dumps(hist+current)
        except Exception as e:
            print "Couldn't save history",e
        self.current = []
        self.store_current(self.current)
        self.available=False
        self.fresh=False
        self.save()
        
    #Returns the current next bit of data to be drawn
    #It is a list of dicts, with each entry having:
    # time: datetime?
    # data fields holding doubles
    # For scalar sources, one data field called val
    def get_current(self) : 
        if not self.current:
            self.current = json.loads(self.current_data)
            for entry in self.current :
                self.deserialise_time(entry)
        return self.current
    
    def get_historic(self):
        historic = json.loads(self.historic_data)
        for entry in historic :
            self.deserialise_time(entry)
        return historic
    
    def get_historic_size(self):
        return len( self.get_historic() )
    def get_current_size(self):
        return len( self.get_current() )
    
    #Adds the data to the current data and sets available to true
    #Data must be a list of dicts 
    def add_data(self,data):
        self.update_current_data(data)
        print "Pre-Pipeline Data",self.get_current()
        print "Data Is:",self.id
        print "Data Hash",hash(self)
        self.clean()
        if hasattr(self, 'pipeline'):
            self.pipeline.update(self)
        print "Post-Pipeline Data",self.get_current()
    
    def update_current_data(self,data):
        print "Adding data:",data
        self.available=True
        self.fresh=True
        for entry in data :
            self.deserialise_time(entry)
        cur = self.get_current()
        total = cur + data
        self.store_current(total)
        self.save()
        print "Saved data:",self.current_data
    
    def clear_all(self):
        self.historic_data = json.dumps([])
        self.current_data = json.dumps([])
        self.current = []
        
    def mark_stale(self):
        self.fresh=False
        self.save()
        
    def load_current(self):
        cur = json.loads(self.current_data)
        return cur
    
    def store_current(self, current ):
        self.current = current or []
        current = deepcopy(self.current)
        for entry in current:
            #print "Before",entry
            self.serialise_time(entry)
            #print "After",entry
        totals = json.dumps(current)
        #print "Storing:",totals
        self.current_data = totals
    
    def serialise_time(self,entry):
        entry['time_ser'] = entry.get('time', timezone.now() ).isoformat()
        if entry.has_key('time'):
            del entry['time']
    
    def deserialise_time(self,entry):
        date_str = entry.get('time',timezone.now().isoformat())
        entry['time'] = dateutil.parser.parse(date_str)
        if entry.has_key('time_ser'):
            del entry['time_ser']
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.id)

    class Meta:
        app_label = 'polargraph'
