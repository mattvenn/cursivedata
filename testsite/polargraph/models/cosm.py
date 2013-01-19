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

#Represents a COSM trigger, and maps it to a data_store, parsing any messages sent
class COSMSource( models.Model ):
    data_store = models.ForeignKey( DataStore )
    feed_id = models.CharField(max_length=400,default="96779")
    stream_id = models.CharField(max_length=400,default="1")
    api_key = models.CharField(max_length=400,default="WsH6oBOmVbflt5ytsSYHYVGQzCaSAKw0Ti92WHZzajZHWT0g")
    cosm_trigger_id = models.CharField(max_length=50,blank=True)
    url_base = models.CharField(max_length=200,default="http://mattvenn.org")
    cosm_url=models.CharField(max_length=200,default="http://api.cosm.com/v2/triggers/")
    
    #Extracts the data from the COSM trigger.
    #We could do something more clever here to stick datastreams together, but this works for now.
    def receive_data(self,msg):
        print "DS:",str(self.data_store_id),"Got message for data_store:",str(msg)
        value = msg["triggering_datastream"]["value"]["value"]
        time = msg["triggering_datastream"]["at"]
        self.data_store.add_data([{"time":time, "value":value}])
        
    def start_trigger(self):
        headers= {'content-type': 'application/json'}
        headers['X-ApiKey'] = self.api_key
        data = { "trigger_type":"change" }
        data["environment_id"]=self.feed_id
        data["stream_id"]=self.stream_id 
        url = self.get_url()
        data["url"]=url
        
        r=requests.post(self.cosm_url,data=json.dumps(data),headers = headers)
        try:
            cosm_trigger_id=r.headers['location'].split("/")[-1]
            print "Setting up COSM trigger",url,"for data_store",self.data_store_id,"with id:",cosm_trigger_id
            print "Pointing to URL:",data['url']
            self.cosm_trigger_id=cosm_trigger_id
            self.save()
            return "OK"
        except Exception as e:
            print "Coudln't setup COSM trigger:",e
            return r
        
    def stop_trigger(self):
        if self.cosm_trigger_id :
            print "Removing trigger"
            requests.delete(self.cosm_url+str(self.cosm_trigger_id),headers={'X-ApiKey':self.api_key})
            self.cosm_trigger_id=""
            self.save()
        else:
            print "Trigger not set"
        
    def get_url(self):
        return self.url_base+"/api/v1/cosm/"+str(self.id)+"/"
    
    class Meta:
        app_label = 'polargraph'