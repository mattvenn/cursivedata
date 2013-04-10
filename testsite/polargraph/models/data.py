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
    historic_data = models.CharField(max_length=40000,default=json.dumps([]))
    available = models.BooleanField(default=False)
    fresh=False
    
    #After the data's been used, add it to the history and clear the current data
    def clear_current(self) : 
        current = json.loads(self.current_data)
        hist = json.loads(self.historic_data)
        self.historic_data=json.dumps(hist+current)
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
    
    def query(self,max_records=None,max_time=None,min_time=None):
        data = self.get_historic() + self.get_current() 
        print "Orig size", len(data)
        if max_time :
            data = filter(lambda d: d["time"].toordinal() < max_time.toordinal(), data)
        if min_time :
            data = filter(lambda d: d["time"].toordinal() > min_time.toordinal(), data)
        if max_records :
            if (len(data) > max_records ):
	            data = data[-max_records:]
        print "Final size", len(data)
        return data
    
    #Adds the data to the current data and sets available to true
    #Data must be a list of dicts 
    def add_data(self,data):
        self.update_current_data(data)
        print "Pre-Pipeline Data length:",len(self.get_current())
        print "Datastore ID is:",self.id
#        print "Data Hash",hash(self)
        self.clean()
        if hasattr(self, 'pipeline'):
            print "Trying to run pipline: ",self.pipeline
            self.pipeline.update(self)
        print "Post-Pipeline Data length:",len(self.get_current())
    
    #this throws an error when its fields get too long, but the error is supressed somewhere
    def update_current_data(self,data):
        print "Adding data:",data
        self.available=True
        self.fresh=True
        for entry in data :
            self.deserialise_time(entry)
        try:
            cur = self.get_current()
            total = cur + data
            self.store_current(total)
            self.save()
            print "Saved data length:",len(self.current_data)
        #this happens because we run out of space FIXME!
        except ValueError:
            print "problem with current data! - wiping it"
            self.clear_all()
            self.save()


    
    def load_from_csv(self,data, time_field=None):
        reader = csv.DictReader(data,skipinitialspace=True)
        data = []
        print "Adding data to store",str(self)
        for row in reader:
            print "Row:",row
            if time_field :
                row['time_ser'] = row[time_field]
                del row[time_field]
            data.append(row)
        self.update_current_data(data)
    
    def load_from_csv_file(self,datafile,time_field=None):
        with open(datafile, 'rb') as csvfile:
            self.load_from_csv(csvfile,time_field)
        
    
    def clear_historic_data(self):
        self.historic_data = json.dumps([])
        self.save()
        
    def clear_all(self):
        self.historic_data = json.dumps([])
        self.current_data = json.dumps([])
        self.current = []
        self.save()
        
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
        if entry.has_key('time_ser'):
            date_str = entry.get('time_ser',timezone.now().isoformat())
            entry['time'] = dateutil.parser.parse(date_str)
            del entry['time_ser']
        elif entry.has_key('time'):
            date_str = entry.get('time',timezone.now().isoformat())
            entry['time'] = dateutil.parser.parse(date_str)
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.id)

    class Meta:
        app_label = 'polargraph'
