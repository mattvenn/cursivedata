#!/usr/bin/python
import SocketServer
import SimpleHTTPServer
import urllib
import os
import datetime
import sys
from TimeStats import TimeStats

nanodeGetTimes = TimeStats()
dir = "/home/matt/polargraphenergymonitor/tmp/46756/"
PORT = 10002

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
    global nanodeGetTimes
    nanodeGetTimes.addTime()
    time_span = 10 * 60
    print >>sys.stderr, '>>>>connection from %s [%d in %dsecs]' % ( self.client_address, nanodeGetTimes.howMany(time_span),time_span)
    if self.client_address[0] == "195.10.248.18":
      print >>sys.stderr, "rejecting request from the hackspace"
      return
    try:
      fh = open(dir+"square.polar")
      print "sending file: square.polar"
      gcode = fh.read()
      fh.close()
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write(gcode)
      #then remove it
      print "moving old file"
      try:
        now = datetime.datetime.now()
        seconds = now.strftime("%s")
        newfile = dir + "/history.polar/" + str(seconds) + ".polar" 
        os.rename(dir+"square.polar", newfile)
      except:
        e = sys.exc_info()[0]
        print "couldn't move file", e
    except:
      print "no new data"
      self.send_response(404)
      self.send_header('Content-type','text/html')
      self.end_headers()
    return

print "serving at port", PORT
server = SocketServer.ThreadingTCPServer(("mattvenn.net", PORT), Proxy,False)
server.allow_reuse_address=True
server.server_bind()
server.server_activate()
server.serve_forever()
