#!/usr/bin/python
from TimeStats import TimeStats
import sys
import subprocess
import json
import argparse
import SocketServer
import SimpleHTTPServer
import urllib
import os
import iso8601
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
    date = iso8601.parse_date(time)
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    day = int(date.strftime("%d") ) # day

    #ten mins
    mins =  (minute + hour * 60)/10 # 0 - 143
    seconds = date.strftime("%s")
#    import pdb;pdb.set_trace()
    wipe = False
    #do we need to start afresh with a new drawing?
    if config[feed].has_key("start_daily") and config[feed].has_key("last_time"):
        last_day = int(config[feed]["last_time"].strftime("%d")) # day
        if last_day != day:
            wipe = True

    #save the date
    config[feed]["last_time"] = date
    
    #tmp dir
    tmp_dir = "../tmp/" + str(feed) + "/"
    generator_args = [ config[feed]["generator"] ]
    generator_args.extend( config[feed]["draw_args"] )
    if wipe:
        generator_args.append( "--wipe" )
    generator_args.extend( [ "--dir", tmp_dir, "--number", str(mins), "--env", str(int(float(light)))])
    if args.debug:
        print >>sys.stderr, "calling generator: %s" % generator_args
    p = subprocess.Popen( generator_args, stdout=subprocess.PIPE )
    stdout,stderr = p.communicate()
    if args.debug:
        print stdout
        if p.returncode == 0:
            print "generator created svg file"

    if p.returncode == 0 and config[feed]["needs_polar"]:
      print >>sys.stderr, "convert svg to gcode"
      #run the pycam stuff here
      pycam_args = [args.pycam, tmp_dir + "square.svg", "--export-gcode=" + tmp_dir + "square.ngc", "--process-path-strategy=engrave"]
      if args.debug:
        print pycam_args
      result = subprocess.call(pycam_args)
      if result == 0: #unix for all good
        print >>sys.stderr, "convert gcode to polar code"
        p = subprocess.Popen(["./preprocess.py", "--force_store", "--file", tmp_dir + "square.ngc"], stdout=subprocess.PIPE)
        gcode,stderr = p.communicate()
        fh = open( tmp_dir + "square.polar", "w" )
        fh.write(gcode)
        fh.close()

        #move the svg file to history with a timestamp
        newfile = tmp_dir + "history/" + str(seconds) + ".svg" 
        os.rename(tmp_dir + "square.svg", newfile)

      else:
        #move the svg file to history with a timestamp
        newfile = tmp_dir + "bustsvg/" + str(seconds) + ".svg" 
        os.rename(tmp_dir + "square.svg", newfile)
        
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


