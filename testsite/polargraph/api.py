'''
Created on 6 Jan 2013

@author: dmrust
'''

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from polargraph.models import DataStore,COSMEndpoint
import django.core.serializers.json
import json
from django.utils import simplejson

class CustomJSONSerializer(Serializer):
    
    def from_json(self, content):
        data = json.loads(content)
        return data
        
    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return simplejson.dumps(data, cls=django.core.serializers.json.DjangoJSONEncoder,
                sort_keys=True, ensure_ascii=False, indent=True)
        
        
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

class COSMEndpointResource(ModelResource):
    class Meta:
        queryset = COSMEndpoint.objects.all()
        resource_name = 'cosm'
        authorization = Authorization()
        serializer = CustomJSONSerializer()
        allowed_methods = ['get','post','patch']
    
    def post_detail(self, request, **kwargs):
        print "ENDPOINT UPDATE!"
        store_id=int(request.path.split("/")[-2])
        ce = COSMEndpoint.objects.get(id=store_id) #Uuuugh. Sorry!
        data=json.loads(request.raw_post_data)
        ce.data_store.add_data(data["input_data"])
        return {"OK":"True"}
    