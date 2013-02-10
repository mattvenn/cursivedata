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
from polargraph.models.data import DataStore
from django.utils.datetime_safe import datetime
import re

#Represents a COSM trigger, and maps it to a data_store, parsing any messages sent
class COSMSource( models.Model ):
    data_store = models.ForeignKey( DataStore )
    feed_id = models.CharField(max_length=400,default="96779")
    stream_id = models.CharField(max_length=400,default="1")
    api_key = models.CharField(max_length=400,default="WsH6oBOmVbflt5ytsSYHYVGQzCaSAKw0Ti92WHZzajZHWT0g")
    cosm_trigger_id = models.CharField(max_length=50,blank=True)
    url_base = models.CharField(max_length=200,default="http://mattvenn.net:8080")
    cosm_url=models.CharField(max_length=200,default="http://api.cosm.com/v2/triggers/")
    #Add in the lat/lon to any data recieved
    add_location = models.BooleanField(default=False)
    #Use the id of the stream as the variable name
    use_stream_id = models.BooleanField(default=False)
    #Add the title of the feed to the data
    add_feed_title = models.BooleanField(default=False)
    #Add the id of the feed to the data
    add_feed_id = models.BooleanField(default=False)
    last_updated = models.DateTimeField("Last Updated",blank=True,null=True)
    
    #Extracts the data from the COSM trigger.
    #We could do something more clever here to stick datastreams together, but this works for now.
    def receive_data(self,msg):
        print "DS:",str(self.data_store_id),"Got message for data_store:",str(msg)
        value = msg["triggering_datastream"]["value"]["value"]
        time = msg["triggering_datastream"]["at"]
        datapoint = {"time":time}
        if self.add_location :
            datapoint['location'] = {}
            datapoint['location']['lat'] = msg["environment"]["location"]["lat"]
            datapoint['location']['lon'] = msg["environment"]["location"]["lng"]
        if self.use_stream_id :
            stream_id = msg["triggering_datastream"]["id"]
            datapoint[stream_id] = value
        else:
            datapoint['value'] = value
        if self.add_feed_id :
            datapoint["feed_id"] = msg["environment"]["id"]
        if self.add_feed_id :
            datapoint["feed_title"] = msg["environment"]["title"]
        self.data_store.add_data([datapoint])
        self.last_updated = timezone.now()
        self.save()
        
    def start_trigger(self):
        headers= {'content-type': 'application/json'}
        headers['X-ApiKey'] = self.api_key
        data = { "trigger_type":"change" }
        data["environment_id"]=self.feed_id
        data["stream_id"]=self.stream_id 
        url = self.get_url()
        if not re.match("^http://",url):
            url = "http://"+url
        data["url"]=url
        
        print "Setting up COSM trigger for data_store",self.data_store_id,\
            " from feed:",self.feed_id,", stream:",self.stream_id,", API Key: ",self.api_key
        print "Pointing to URL:",data['url']
        r=requests.post(self.cosm_url,data=json.dumps(data),headers = headers)
        try:
            cosm_trigger_id=r.headers['location'].split("/")[-1]
            print "Setup with id:",cosm_trigger_id
            self.cosm_trigger_id=cosm_trigger_id
            self.save()
            return "OK"
        except Exception as e:
            print "Coudln't setup COSM trigger:",e
            print "Sent to url:",self.cosm_url
            print "Sent data:",json.dumps(data)
            print "Response:",r
            print "Headers:",r.headers
            return r
        
    def stop_trigger(self):
        if self.cosm_trigger_id :
            print "Removing trigger"
            requests.delete(self.cosm_url+str(self.cosm_trigger_id),headers={'X-ApiKey':self.api_key})
            self.cosm_trigger_id=""
            self.save()
        else:
            print "Trigger not set"
    def is_running(self):
        if self.cosm_trigger_id:
            return True
        return False
        
    def get_url(self):
        return self.url_base+"/api/v1/cosm/"+str(self.id)+"/"
    
    class Meta:
        app_label = 'polargraph'
