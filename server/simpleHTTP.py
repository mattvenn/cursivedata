#!/usr/bin/python
import SocketServer
import SimpleHTTPServer
import urllib
import os
import datetime
import sys
from TimeStats import TimeStats

nanodeGetTimes = TimeStats()
file="square.polar"
dir = "/home/mattvenn/polargraphenergymonitor/tmp/46756/" 
PORT = 10002

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
    global nanodeGetTimes
    nanodeGetTimes.addTime()
    time_span = 10 * 60
    print >>sys.stderr, '>>>>connection from %s [%d in %dsecs]' % ( self.client_address, nanodeGetTimes.howMany(time_span),time_span)
    try:
      fh = open(dir+file)
      gcode = fh.read()
      print "sending file %s, %d bytes" %( file, len(gcode))
      fh.close()
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write(gcode)
      self.wfile.close()
      """
      #then remove it
      print "moving old file"
      try:
        now = datetime.datetime.now()
        seconds = now.strftime("%s")
        newfile = "./oldpolar/" + str(seconds) + ".polar" 
        os.rename(dir+"square.polar", newfile)
      except:
        e = sys.exc_info()[0]
        print "couldn't move file", e
      """
      #TODO: sort this global except done
    except IOError:
      print "no new data"
      self.send_response(404)
      self.send_header('Content-type','text/html')
      self.end_headers()
    return

print "serving at port", PORT
server = SocketServer.ThreadingTCPServer(("192.168.0.100", PORT), Proxy,False)
server.allow_reuse_address=True
server.server_bind()
server.server_activate()
server.serve_forever()
