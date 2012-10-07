#!/usr/bin/python
import SocketServer
import SimpleHTTPServer
import urllib
import os
import datetime
import sys
from TimeStats import TimeStats

nanodeGetTimes = TimeStats()

PORT = 10002

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
    global nanodeGetTimes
    nanodeGetTimes.addTime()
    time_span = 10 * 60
    print >>sys.stderr, '>>>>connection from %s [%d in %dsecs]' % ( self.client_address, nanodeGetTimes.howMany(time_span),time_span)
    try:
      #filename = sorted( os.listdir("newpolar") )[0]
      fh = open("square.polar")
#      oldfile = "./newpolar/" + filename
#      fh = open( oldfile )
      print "sending file" #,  oldfile
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
        newfile = "./oldpolar/" + str(seconds) + ".polar" 
        os.rename("square.polar", newfile)
#        newfile = "./oldpolar/" + filename
#        os.rename( oldfile, newfile)
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