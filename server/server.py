#!/usr/bin/python
from TimeStats import TimeStats
import sys
import json
import argparse
import SocketServer
import SimpleHTTPServer
import urllib
import os

from config import config
  
#how to do this properly?
cosmPostTimes = TimeStats()


def extractData(line):
    jsondata = urllib.unquote(line)
    trigger = json.loads(jsondata.lstrip("body="))
    light = trigger["triggering_datastream"]["value"]["value"]
    time = trigger["triggering_datastream"]["at"]
    feed = trigger["environment"]["id"]
    if args.debug:
        print "got %s at %s for feed %s" % ( light, time, feed )
    return (light,time, feed)

def processData((light,time,feed)):
    global args
    import iso8601
    date = iso8601.parse_date(time)
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    #ten mins
    mins =  (minute + hour * 60)/10 # 0 - 143
    seconds = date.strftime("%s")

    import subprocess
    args = [ config[feed]["generator"] ]
    args.extend( config[feed]["draw_args"] )
    args.extend( [ "--number", str(mins), "--env", str(int(float(light)))])
    print >>sys.stderr, "calling generator: %s" % args
    p = subprocess.Popen( args, stdout=subprocess.PIPE )
    stdout, result = p.communicate()
    if args.debug:
        print stdout
    if result == 0 and config[feed]["needs_polar"]:
      print >>sys.stderr, "new svg"
      #run the pycam stuff here
      result = subprocess.call([args.pycam, "square.svg", "--export-gcode=square.ngc", "--process-path-strategy=engrave"])
      if result == 0: #unix for all good
        print >>sys.stderr, "process gcode to polar code"
        p = subprocess.Popen(["./preprocess.py", "--file", "square.ngc"], stdout=subprocess.PIPE)
        gcode, err = p.communicate()
        fh = open( "square.polar", "w" )
        fh.write(gcode)
        fh.close()
        print "written polar code"

        #move the svg file to history with a timestamp
        newfile = "./history/" + str(seconds) + ".svg" 
        os.rename("square.svg", newfile)

      else:
        #move the svg file to history with a timestamp
        newfile = "./bustsvg/" + str(seconds) + ".svg" 
        os.rename("square.svg", newfile)
    else:
        print "no svg"
        
class postHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        global cosmPostTimes
        cosmPostTimes.addTime()
        time_span = 10 * 60
        print >>sys.stderr, '>>>>connection from %s [%d in %dsecs]' % ( self.client_address, cosmPostTimes.howMany(time_span),time_span)
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        processData( extractData(post_body) )
        return

def run_server(args):
    # Bind the socket to the port
    server_address = (args.hostname, args.port)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    server = SocketServer.ThreadingTCPServer(server_address, postHandler,False)
    server.allow_reuse_address=True
    server.server_bind()
    server.server_activate()
    server.serve_forever()

if __name__ == '__main__':
  argparser = argparse.ArgumentParser(
      description="listens for updates from cosm and turns them into gcodes by running an external program")
  argparser.add_argument('--hostname',
      action='store', dest='hostname', default="localhost",
      help="hostname")
  argparser.add_argument('--port',
      action='store', dest='port', type=int, default=10001,
      help="port")
  argparser.add_argument('--pycam',
      action='store', dest='pycam', default="/usr/bin/pycam",
      help="where pycam is")
  argparser.add_argument('--debug',
      action='store_const', const=True, dest='debug', default=False,
      help="debug print")

  args = argparser.parse_args()
  run_server(args)


