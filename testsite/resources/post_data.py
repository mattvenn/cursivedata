import requests
import json
import pprint
import argparse


def push_data():
    headers= {'content-type': 'application/json'}
      #"timestamp": "$TIME",
      #how much of this can be got rid of?
    data = {
      "environment": 
      {
        "description": "",
        "feed": "http:\/\/api.cosm.com\/v2\/feeds\/343",
        "id": 343,
        "location": 
        {
          "lat": 55.74479,
          "lng": -3.18157,
          "name": "location description"
        },
        "title": "test feed yes"
      },
      "id": 1,
      "threshold_value": 9.0,
      "triggering_datastream": 
      {
        "id": "0",
        "url": "http:\/\/api.cosm.com\/v2\/feeds\/343\/datastreams\/0",
        "at": "2009-09-07T12:16:02.000063Z",
        "value": 
        {
          "value": args.value,
          "max_value": 9.99650150341,
          "min_value": 0.00471012639984
        }
      },
      "type": "gte",
      "url": "http:\/\/api.cosm.com\/v2\/triggers\/1"
    }

    r = requests.post(args.url + str(args.pipeline) + "/",headers=headers,data=json.dumps(data))
    print r.status_code
    try:
        pprint.pprint(json.loads(r.text))
    except:
        print r.text

if __name__ == '__main__':

    default_url = 'http://localhost:8080/api/v1/cosm/'
#    'http://mattvenn.net:8080/api/v1/cosm'

    parser = argparse.ArgumentParser(description="feed polar files to polargraph robot")
    parser.add_argument('--pipeline',
        action='store', dest='pipeline', type=int, default='1',
        help="pipeline")
    parser.add_argument('--value',
        action='store', dest='value', type=float, default='1',
        help="value")
    parser.add_argument('--url',
        action='store', dest='url', default=default_url,
        help="url of the api")

    args = parser.parse_args()
    print args.url
    push_data()
