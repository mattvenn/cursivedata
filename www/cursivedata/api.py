'''
Created on 6 Jan 2013

@author: dmrust
'''

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from cursivedata.models import DataStore, COSMSource, Endpoint, Pipeline
import django.core.serializers.json
import json
from django.utils import simplejson
from django.http import QueryDict
from django.utils import timezone

import logging
log = logging.getLogger('api')

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
        log.debug("Adding data to:%s" % store.name)
        store.add_data(bundle.data["input_data"])
        store.save()
        return store

class COSMSourceResource(ModelResource):
    class Meta:
        queryset = COSMSource.objects.all()
        resource_name = 'cosm'
        authorization = Authorization()
        serializer = CustomJSONSerializer()
        allowed_methods = ['get','post','patch']
    
    def post_detail(self, request, **kwargs):
        store_id=int(request.path.split("/")[-2])
        log.info("cosm update for datastore %d" % store_id)
        ce = COSMSource.objects.get(id=store_id)  # Uuuugh. Sorry!
        data_string = request.POST.get('body') or request.raw_post_data
        data = json.loads(data_string)
        log.debug("data is %s" % data)
        try:
            ce.receive_data(data)
            return {"OK":"True"}
        except Exception as e:
            log.exception("cosm update failed: %s" % str(e))
    
class EndpointResource(ModelResource):
    class Meta:
        queryset = Endpoint.objects.all()
        resource_name = 'endpoint'
        authorization = Authorization()
        serializer = CustomJSONSerializer()
        allowed_methods = ['get','patch']

    def obj_update(self, bundle, request=None, **kwargs):
        res = super(EndpointResource, self).obj_update(bundle, request, **kwargs)
        endpoint = bundle.obj
        endpoint.status_updated = timezone.now()
        endpoint.save() 
        log.info("endpoint %s updated: %s" % (endpoint.id, endpoint.status_updated))
        return res
