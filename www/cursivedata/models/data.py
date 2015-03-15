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
import cursivedata.svg as svg
import requests
import dateutil.parser
import jsonfield




#This takes in data that's been produced by some process and a) makes current stuff
#available, and b) stores historic values
#Has a flag to say if there's new data to be used
# Data format is a list of dicts. Each dict has a time field, containing the time it was created.
# When data is added, if it doesn't have a time, the current time is used
# When you get the data, all the time fields will be datetime objects
class DataStore( models.Model ) :
    name = models.CharField(max_length=200)
    available = models.BooleanField(default=False)
    fresh=False
    
    #After the data's been used, add it to the history and clear the current data
    def clear_current(self):
        for datapoint in DataPoint.objects.filter(current=True, datastore=self) :
            datapoint.current=False
            datapoint.save()
            
        self.available=False
        self.fresh=False
        self.save()
        
    #Returns the current next bit of data to be drawn
    #It is a list of dicts, with each entry having:
    # time: datetime?
    # data fields holding doubles
    # For scalar sources, one data field called val
    def get_current(self) : 
        return DataPoint.objects.filter(current=True, datastore=self).order_by('id')
    
    def get_historic(self):
        return DataPoint.objects.filter(current=False, datastore=self).order_by('id')
    
    def get_historic_size(self):
        return DataPoint.objects.filter(current=False, datastore=self).count()

    def get_current_size(self):
        return DataPoint.objects.filter(current=True, datastore=self).count()
    
    def query(self,max_records=None,max_time=None,min_time=None):

        #last part nasty because data doesn't support negative indexing
        if min_time and max_time:
            data = DataPoint.objects.filter(date__range=[min_time,max_time] , datastore=self).order_by('-id')[:max_records]
        elif min_time:
            data = DataPoint.objects.filter(date__gt=min_time , datastore=self).order_by('-id')[:max_records]
        elif max_time:
            data = DataPoint.objects.filter(date__lt=max_time , datastore=self).order_by('-id')[:max_records]
        else:
            data = DataPoint.objects.filter( datastore=self).order_by('-id')[:max_records]
        #data = DataPoint.objects.filter( datastore=self).order_by('-id')[:max_records]
        print "Final size", len(data)
        return data.reverse()
    
    #Adds the data to the current data and sets available to true
    #Data must be a list of dicts 
    def add_data(self,data):
        self.update_current_data(data)
        print "Pre-Pipeline Data length:",len(self.get_current())
        print "Datastore ID is:",self.id
#        print "Data Hash",hash(self)
        self.clean()
        if hasattr(self, 'pipeline'):
            print "Trying to run pipeline:",self.pipeline
            self.pipeline.update(self)
        else:
            print "datastore has no pipeline to run"
        print "Post-Pipeline Data length:",len(self.get_current())
    
    #data is a list with each member containing a date and a data field
    def update_current_data(self,data):
        print "Adding %d lines of data:" % len(data)
        self.available=True
        self.fresh=True
        for entry in data :
            #Make a new DataPoint with the given time and data
            datapoint = DataPoint(data=entry["data"],date=entry["date"],current=True,datastore=self)
            #Save it
            datapoint.save()

    
    def load_from_csv(self,data, time_field=None):
        reader = csv.DictReader(data,skipinitialspace=True)
        data = []
        print "Adding data to store",str(self)
        for row in reader:
            #check we have a value
            if not row.has_key('value'):
                raise ValueError
            #Create a dict with {date=date, data=data} and append
            datapoint = {}
            if time_field :
                datapoint['date'] = row[time_field]
                del row[time_field]
            else:
                datapoint['date'] = timezone.now()
            datapoint['data'] = row
            

            data.append(datapoint)
        print "loaded %d lines" % len(data)
        self.update_current_data(data)
    
    def load_from_csv_file(self,datafile,time_field=None):
        with open(datafile, 'rb') as csvfile:
            self.load_from_csv(csvfile,time_field)
        
    
    def clear_historic_data(self):
        DataPoint.objects.filter(current=False, datastore=self).delete()
        
    def clear_all(self):
        DataPoint.objects.filter(datastore=self).delete()
        
    def mark_stale(self):
        self.fresh=False
        self.save()
        
    """ 
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
    
    """
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.id)

    class Meta:
        app_label = 'cursivedata'

class FakeDataStore(DataStore):
    def load_data(self,data):
        self.current = data
    def get_current(self):
        return self.current
    
#store data in a separate table
class DataPoint( models.Model ):
    data = jsonfield.JSONField(default={})
    date = models.DateTimeField(default=timezone.now)
    datastore = models.ForeignKey( DataStore )
    current = models.BooleanField(default=True)

    def getStreamName(self):
        #return first key
        if len(self.data.keys()) > 1:
            raise Exception("we got a datapoint with more than 1 data value in it")
        return self.data.keys()[0]

    def getValue(self):
        return self.data[self.getStreamName()]

    class Meta:
        app_label = 'cursivedata'

