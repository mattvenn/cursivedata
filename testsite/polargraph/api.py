'''
Created on 6 Jan 2013

@author: dmrust
'''

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from polargraph.models import DataStore
#from django.core.serializers import json
import json
from django.utils import simplejson
import time

class CustomJSONSerializer(Serializer):
    
    def from_json(self, content):
        data = json.loads(content)
        return data
        
        
        
class DataStoreResource(ModelResource):
    class Meta:
        queryset = DataStore.objects.all()
        resource_name = 'datastore'
        authorization = Authorization()
        serializer = CustomJSONSerializer()
        allowed_methods = ['get','patch']
    
    #Special update - only allows adding data in the "input data" field
    def obj_update(self, bundle, request=None, **kwargs):
        store = bundle.obj
        print "Adding data to:",store.name
        store.add_data(bundle.data["input_data"])
        store.save()
        return store

