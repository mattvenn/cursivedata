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
from cursivedata.models.data import DataStore
from django.utils.datetime_safe import datetime
import re
import logging
log = logging.getLogger('data')

#Represents a COSM trigger which can be connected to any pipelines
class COSMSource( models.Model ):
    name = models.CharField(max_length=100,default="Unknown Source")
    pipelines = models.ManyToManyField( 'Pipeline', blank=True )
    feed_id = models.CharField(max_length=400,default="96779")
    stream_id = models.CharField(max_length=400,default="1")
    api_key = models.CharField(max_length=400,default="WsH6oBOmVbflt5ytsSYHYVGQzCaSAKw0Ti92WHZzajZHWT0g")
    cosm_trigger_id = models.CharField(max_length=50,blank=True)
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
    last_value = models.CharField(max_length=200,default="")
    
    #Extracts the data from the COSM trigger.
    #We could do something more clever here to stick datastreams together, but this works for now.
    def receive_data(self,msg):
        log.debug( "got data %s" % msg)
        value = msg["triggering_datastream"]["value"]["value"]
        time = msg["triggering_datastream"]["at"]
        datapoint = {}

        # make a note of this in case an exception happens later on
        self.last_updated = timezone.now()
        self.last_value = value
        self.save()

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
        data = {"date":time,"data":datapoint}
        for pipeline in self.pipelines.all():
            pipeline.add_data([data])
        self.last_updated = timezone.now()
        self.last_value = value
        self.save()
        
    #returns true if updated within last hour
    @property
    def is_live(self):
        live_date = timezone.now()-timezone.timedelta(hours=1)
        if self.last_updated > live_date:
            return True
        return False

    def start_trigger(self,domain,port):
        headers= {'content-type': 'application/json'}
        headers['X-ApiKey'] = self.api_key
        data = { "trigger_type":"change" }
        data["environment_id"]=self.feed_id
        data["stream_id"]=self.stream_id 
#        import ipdb; ipdb.set_trace()
        domain = 'cursivedata.co.uk'
        port = '80'
        url = self.get_url(domain,port)
        if not re.match("^http://",url):
            url = "http://"+url
        data["url"]=url
        
        log.info("Setting up COSM trigger for pipelines %s from feed %s stream %s key %s" % (self.pipelines ,self.feed_id, self.stream_id, self.api_key))
        log.info("Pointing to URL %s" % data['url'])
        r=requests.post(self.cosm_url,data=json.dumps(data),headers = headers)
        if r.status_code == 201:
            cosm_trigger_id=r.headers['location'].split("/")[-1]
            log.info("Setup with id: %s" % cosm_trigger_id)
            self.cosm_trigger_id=cosm_trigger_id
            self.save()
            return "OK"
        elif r.status_code == 404:
            log.warning("no such stream id, check stream id")
        elif r.status_code == 401:
            log.warning("not authorized, check api key")
        elif r.status_code == 500:
            log.warning("no such data stream, check environment id")
        else:
            log.warning("unknown error: %d %s" % (r.status_code, json.loads(r.text)))
        
    def stop_trigger(self):
        if self.cosm_trigger_id :
            log.info("Removing trigger")
            requests.delete(self.cosm_url+str(self.cosm_trigger_id),headers={'X-ApiKey':self.api_key})
            self.cosm_trigger_id=""
            self.save()
        else:
            log.info("Trigger not set")

    def is_running(self):
        if self.cosm_trigger_id:
            return True
        return False
        
    def get_url(self,domain,port):
        return domain + ":" + port +"/api/v1/cosm/"+str(self.id)+"/"
    
    class Meta:
        app_label = 'cursivedata'

    def __unicode__(self):
        return "Cosm: "+self.name+" ("+self.cosm_trigger_id+")"
