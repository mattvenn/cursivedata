import requests
import json
import pprint
data = {}

url="http://api.cosm.com/v2/triggers/"

f = open("cosm_create_trigger.json.bust")
data = json.load(f)
print data
print "make trigger----------"
r = requests.post(url,data=json.dumps(data["data"]),headers=data["headers"])
print r.status_code
try:
    a = json.loads(r.text)
    pprint.pprint(a)
except ValueError:
    pass

print "make request----------"
r = requests.get(url,headers=data["headers"])
print r.status_code
try:
    a = json.loads(r.text)
    pprint.pprint(a)
except ValueError:
    pass
