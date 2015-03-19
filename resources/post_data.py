#!/usr/bin/python
import random
import time
import requests
import json
import datetime
import pprint
import argparse
import sys

def push_data( input_data ):
    headers= {'content-type': 'application/json'}
    print "value: ", args.value
    data = {
        "input_data": input_data,
        "name": "UPDATED!"
        }
    r = requests.patch(args.url + str(args.datastore) + "/",headers=headers,data=json.dumps(data))
    print r.status_code
    if r.text:
        try:
            dat = json.loads(r.text)
            if dat.has_key('traceback'):
                print dat["traceback"]
        except:
            print >>sys.stderr, r.text
            raise

def calculate_datetime_from_minute(minute):
   now = datetime.datetime.now()
   if minute:
       print "minute", minute
       hours = int(minute / 60)
       mins = minute % 60
       then = datetime.datetime(now.year,now.month,now.day,hours,mins,0) 
   else:
       then = now
   return then.strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == '__main__':

    default_url = 'http://localhost:8000/api/v1/datastore/'
#    'http://mattvenn.net:8080/api/v1/cosm'

    parser = argparse.ArgumentParser(description="feed polar files to polargraph robot")
    parser.add_argument('--datastore',
        action='store', dest='datastore', type=int, default='1',
        help="the id of the datastore (not the pipeline)")
    parser.add_argument('--value',
        action='store', dest='value', type=float, default='1',
        help="value")
    parser.add_argument('--url',
        action='store', dest='url', default=default_url,
        help="url of the api")
    parser.add_argument('--minute',
        action='store', dest='minute', type=int, default='0',
        help="specify a minute of the day to set date to")
    parser.add_argument('--random',
        action='store', dest='random', type=int, default=None,
        help="create random data")
    parser.add_argument('--file',
        action='store', dest='file', help="historical data")
    parser.add_argument('--stream-id',
        action='store', dest='stream_id', help="which stream in historical data")

    args = parser.parse_args()
    print args.url

    if args.file:
        data = json.load(open(args.file))
        if data.has_key(args.stream_id):
            #could we do this all in one go?
            for line in data[args.stream_id]:
                print line
                print line["value"]
                print line["at"]
                push_data([{"data": '{"value":%s}' % line["value"],"date":line["at"]}],)
        else:
            print "no such stream_id, choose from ", data.keys()
    elif args.random:
        #generate random data

        last_min = 0
        last_value = 0
        for i in range(args.random):
            minute = last_min + random.randint(5,15)
            #timestamp = calculate_datetime_from_minute(minute)
            timestamp = calculate_datetime_from_minute(0)
            value = last_value + random.randint(3,10)
            data = [{"data": '{"value":%d}' % value,"date":timestamp}]
            print data
            push_data(data)
            last_value = value
            last_min = minute
    elif args.minute:
        timestamp = calculate_datetime_from_minute(args.minute)
        data = [{"data": '{"value":%d}' % args.value,"date":timestamp}]
        print data
        push_data(data)
    else:
        timestamp = calculate_datetime_from_minute(args.minute)
        push_data([{"data": '{"value":%d}' % args.value,"date":timestamp}],)
