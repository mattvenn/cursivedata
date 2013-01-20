#!/usr/bin/python
import requests
import json

url = 'http://mattvenn.net:8080/api/v1/endpoint/1/' 
payload = {'width': 500}
headers = {'content-type': 'application/json'}
print "PATCH..."
r = requests.patch(url, data=json.dumps(payload),headers=headers)
print r.status_code
print r.text
print "GET..."
r = requests.get(url, headers=headers)
print r.status_code
print r.text
