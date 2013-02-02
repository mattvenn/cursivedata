import requests
import json
import pprint
data = {}

url="http://api.cosm.com/v2/triggers/"
key='bZEYm4Ws0V1pKAg8SOWjD_-V156SAKw4MmNNMkhGZzFTQT0g'

headers= {'content-type': 'application/json'}
headers['X-ApiKey'] = key

r = requests.get(url,headers=headers)
print r.status_code
a = json.loads(r.text)
pprint.pprint(a)
