#!/usr/bin/python
import SocketServer
import SimpleHTTPServer
import urllib
import os
import datetime
import sys
import argparse
from TimeStats import TimeStats

nanodeGetTimes = TimeStats()

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
    global nanodeGetTimes
    nanodeGetTimes.addTime()
    time_span = 10 * 60
    print >>sys.stderr, '>>>>connection from %s [%d in %dsecs]' % ( self.client_address, nanodeGetTimes.howMany(time_span),time_span)
    try:
      fh = open(args.dir+args.file)
      print "sending file: ", args.file
      gcode = fh.read()
      fh.close()
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write(gcode)
      #then remove it if necessary
      if not args.noremove:
          try:
            now = datetime.datetime.now()
            seconds = now.strftime("%s")
            newfile = "./oldpolar/" + str(seconds) + ".polar" 
            print "moving old file to: ", newfile
            os.rename(args.dir+args.file, newfile)
          except OSError, e:
            print "couldn't move file", e
    except IOError, e:
      print "no new data", e
      self.send_response(404)
      self.send_header('Content-type','text/html')
      self.end_headers()
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="serves the polargraph files to the robot and then archives them",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir',
        action='store', dest='dir', default="/home/matt/polargraphenergymonitor/tmp/46756/",
        help="where the file is to be served, and the archive directory")
    parser.add_argument('--file',
        action='store', dest='file', default="square.polar",
        help="the file to send")
    parser.add_argument('--hostname',
        action='store', dest='hostname', default="mattvenn.net",
        help="hostname to listen on")
    parser.add_argument('--port',
        action='store', dest='port', type=int, default=10002,
        help="tcp port to listen on")
    parser.add_argument('--no-remove',
        action='store_const', const=True, dest='noremove', default=False,
        help="don't remove the file after serving, useful for testing")
    parser.add_argument('--verbose',
        action='store_const', const=True, dest='verbose', default=False,
        help="verbose")

    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print "no such directory: ", args.dir
        exit(1)

    print "serving at %s:%d" % (args.hostname, args.port)
    server = SocketServer.ThreadingTCPServer((args.hostname, args.port), Proxy,False)
    server.allow_reuse_address=True
    server.server_bind()
    server.server_activate()
    server.serve_forever()
