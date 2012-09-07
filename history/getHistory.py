#!/usr/bin/python
import urllib
import urllib2
import datetime
import json
import iso8601
import dateutil.parser
import argparse

def fetchRange(start_date,end_date):
    alldatapoints = []
    per_page = 500 #seems limited to 500, tho docs say 1000
    feed_number = 46756
    url = 'http://api.cosm.com/v2/feeds/%d.json' % feed_number

    while start_date < end_date:
        page = 1
        datafeeds_per_feed = 2
        while True:
            values = {
                      'start' : start_date.isoformat(),
                      'duration' : "6hours",
                      'interval' : 0, #once a minute. 0 is everything but can only get 6 hours at a time
                      'key' : "QHcIMwn4vsbSC3kgzClHrh_3XdiSAKw0b1dvY1VBV3JQRT0g",
                      'per_page' : per_page,
                      'page' : page,
                      }

            data = urllib.urlencode(values)
            fullurl = url + '?' + data
            req = urllib2.Request(fullurl)
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
            try:
                datapoints = data["datastreams"][0]["datapoints"] #the 0 is for light
                alldatapoints = alldatapoints + datapoints
                print "got %d datapoints" % len(datapoints)
            except KeyError:
                print "no data points for that period"
                break

            page += 1
            if len(datapoints) != per_page / datafeeds_per_feed:
                print "starting new request"
                break;


        last_date = dateutil.parser.parse(datapoints[len(datapoints)-1]["at"])
        print "date of last datapoint %s" % last_date
        start_date = start_date + datetime.timedelta(hours=6)

    return alldatapoints

if __name__ == '__main__':
  argparser = argparse.ArgumentParser(
      description="fetches historical data from cosm")
  argparser.add_argument('--start',
    action='store', dest='start',
      help="start date")
  argparser.add_argument('--end',
      action='store', dest='end',
      help="end date")

  args = argparser.parse_args()
  if not ( args.start and args.end ):
    print "must provide start and end date"
    exit(1)
  start_date = dateutil.parser.parse(args.start)
  end_date = dateutil.parser.parse(args.end)

  data = fetchRange(start_date,end_date)
  print len(data)
  savefh=open("history.json","w")
  json.dump(data,savefh)
