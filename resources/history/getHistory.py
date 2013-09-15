#!/usr/bin/env python
"""
limitations:
    can only fetches data in chunks of 6 hours

"""
import urllib
import urllib2
import datetime
import json
import iso8601
import dateutil.parser
import argparse

def fetchRange(start_date,end_date,key,feed_number):
    alldatapoints = {}
    per_page = 500 #seems limited to 500, tho docs say 1000
    url = 'http://api.cosm.com/v2/feeds/%d.json' % feed_number

    while start_date < end_date:
        page = 1
        while True:
            values = {
                      'start' : start_date.isoformat(),
                      'duration' : "6hours",
                      'interval' : args.interval, #once a minute. 0 is everything but can only get 6 hours at a time
                      'key' : key,
                      'per_page' : per_page,
                      'page' : page,
                      }

            data = urllib.urlencode(values)
            fullurl = url + '?' + data
            print values["page"], values["start"] 
            req = urllib2.Request(fullurl)
            if args.verbose:
                print values

            response = None
            while response == None:
                try:
                    response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                    print e.code
                    print e.read()
                    print "trying again..."

            the_page = response.read()

            data = json.loads(the_page)
            datapoints = 0
            try:
                for datastream in data["datastreams"]:
                    feed_id = datastream["id"]
                    #create key array if necessary
                    if not alldatapoints.has_key(feed_id):
                        alldatapoints[feed_id] = []
                    alldatapoints[feed_id] = alldatapoints[feed_id] + datastream["datapoints"]
                    datapoints += len(datastream["datapoints"])

                if args.verbose:
                    print "got %d datapoints in %d streams" % (datapoints, len(data["datastreams"]) )
                page += 1

                if datapoints != per_page:
                    break;

            except KeyError:
                print "no data points for that period:", data
                break

        start_date = start_date + datetime.timedelta(hours=6)

    return alldatapoints

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description="fetches historical data from cosm")
    argparser.add_argument('--keyfile',
        action='store', dest='keyfile', default="api.key",
        help="where the api key is stored")
    argparser.add_argument('--feed',
        action='store', dest='feed', type=int, default = 46756, #default is for bristol hackspace
        help="feed number")
    argparser.add_argument('--interval', 
        action='store', dest='interval', default=0, type=int,
        help="interval between datapoints in seconds, 0 for everything")
    argparser.add_argument('--start',
        action='store', dest='start',
        help="start date")
    argparser.add_argument('--end',
        action='store', dest='end',
        help="end date")
    argparser.add_argument('--csv', default=True,
        action='store_const', const=True, dest='csv',
        help="output as csv")
    argparser.add_argument('--json', default=False,
        action='store_const', const=True, dest='json',
        help="output as json")
    argparser.add_argument('--verbose', default=False,
        action='store_const', const=True, dest='verbose',
        help="more verbose output")
    argparser.add_argument('--key', 
        action='store', dest='key',
        help="with csv, only dump the given key")

    args = argparser.parse_args()

    print "using feed number:", args.feed

    #load keyfile
    try:
        keyfile = open(args.keyfile)
        key = keyfile.read()
        key = key.strip()
        print "using key:", key
    except Exception as e:
        print "couldn't open key file '%s': %s" % (args.keyfile, e)
        exit(1)

    #check dates
    if not ( args.start and args.end ):
        print "must provide start and end date"
        exit(1)

    #parse dates
    start_date = dateutil.parser.parse(args.start,dayfirst=True)
    end_date = dateutil.parser.parse(args.end,dayfirst=True)

    #fetch data
    data = fetchRange(start_date,end_date,key,args.feed)
    #import ipdb; ipdb.set_trace()

    #make a summary
    for key in data.keys():
        print "got %d points in feed %s" % ( len(data[key]), key )
   
    if args.key:
        if not data.has_key(args.key):
            print "no such key in data. Choose from", data.keys()
            exit(1)
        keys = [args.key]
    else:
        keys = data.keys()

    if args.json:
        print "storing to history.json"
        fh=open("history.json","w")
        json.dump(data,fh)

    if args.csv:
        print "storing %d keys to history.csv" % len(keys)
        fh=open("history.csv",'w')
        
        #print header
        if args.key:
            fh.write("Time,value\n")
        else:
            fh.write("time,")
            for key in keys:
                fh.write("%s," % (key))
            fh.write("\n")

        first_key = keys[0]
        datapoints = len(data[first_key])

        for line in range(0, datapoints):
            fh.write("%s," % data[first_key][line]["at"])
            #print all keys
            for key in keys:
                try:
                    fh.write("%s," % data[key][line]["value"])
                except:
                    fh.write("0")
            fh.write("\n")
