#!/usr/bin/python
import random
import time
import requests
import json
import datetime
import pprint
import argparse
import sys
import csv

def push_data( input_data ):

    headers= {'content-type': 'application/json'}
    print(input_data)
    if args.test:
        return
    data = {
        "input_data": input_data,
        "name": "UPDATED!"
        }
    r = requests.patch(url + str(args.datastore) + "/",headers=headers,data=json.dumps(data))
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

    parser = argparse.ArgumentParser(description="post data to a datastore")
    parser.add_argument('--host',
        action='store', dest='host', default='localhost',
        help="host url to connect")
    parser.add_argument('--port',
        action='store', dest='port', type=int, default='8000',
        help="port of url")
    parser.add_argument('--datastore',
        action='store', dest='datastore', type=int, default='1',
        help="the id of the datastore (not the pipeline)")
    parser.add_argument('--key',
        action='store', dest='key', default='value',
        help="the key of the data - default is 'value'")
    parser.add_argument('--value',
        action='store', dest='value', type=float, default='1',
        help="value")
    parser.add_argument('--pause',
        action='store', dest='pause', type=int, default='0',
        help="specify num seconds to wait between each post")
    parser.add_argument('--minute',
        action='store', dest='minute', type=int, default='0',
        help="specify a minute of the day to set date to")
    parser.add_argument('--random',
        action='store', type=int, help="create a number of random data points")
    parser.add_argument('--test',
        action='store_const', const=True, help="just print data, don't post it")
    parser.add_argument('--file',
        action='store', dest='file', help="historical data as json, needs stream-id and optionally length")
    parser.add_argument('--length',
        action='store', dest='length', type=int, default='0',
        help="number of records in a file to send")
    parser.add_argument('--stream-id',
        action='store', dest='stream_id', help="comma separated list of streams in historical data")


    args = parser.parse_args()
    url = 'http://%s:%d/api/v1/datastore/' % (args.host, args.port)
    print url

    if args.file:
        if not args.stream_id:
            print('must provide at least one key using stream-id')
            exit(1)
        if ',' in args.stream_id:
            keys = args.stream_id.split(',')
        else:
            keys = [args.stream_id]
        records = 0

        with open(args.file) as fh:
            csv_reader = csv.reader(fh)
            fields = csv_reader.next()
            try:
                for row in csv_reader:
                    for field in keys:
                        index = fields.index(field)
                        push_data([{"data": '{"%s":%f}' % (field,float(row[index])),"date":row[0]}],)
                        time.sleep(args.pause)

                    records += 1
                    if args.length and records >= args.length:
                        break
            except ValueError as e:
                print("%s\nno such field [%s], choose from %s" % (e, field,fields))
                exit(1)
            print("posted %d records" % records)
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
            #print data
            push_data(data)
            last_value = value
            last_min = minute
    else:
        timestamp = calculate_datetime_from_minute(args.minute)
        push_data([{"data": '{"%s":%f}' % (args.key,float(args.value)),"date":timestamp}],)
