#!/usr/bin/python
"""
main problem with reading and writing to the robot is that if we read too much we hang.
if we don't read enough, the leonardo resets!
"""
import urllib
import urllib2
import sys
import re
import sys
import tty
import time
import string
import argparse
import signal
import socket
import serial
TIMEOUT = 0.5 # number of seconds your want for timeout

def fetch_data(args):
    if args.verbose:
        print "fetching from ", args.server
    req = urllib2.Request(args.server)
    try:
        response = urllib2.urlopen(req)
        gcodes = response.read()
        import pdb; pdb.set_trace()
        if args.verbose:
            print "got answer from server:"
            print gcodes
        return gcodes.splitlines()
    except urllib2.URLError, e:
        print >>sys.stderr, e.code
        print >>sys.stderr, e.read()
        return None


def finish_serial():
  if serial:
      print "closing serial"
      print serial
      serial.close()

"""
this requires the robot to respond in the expected way, where all responsed end with "ok"
"""
def readResponse(args,serial,timeout=3):

  response = ""
  while string.find(response,"ok"):
    try:
      response = serial.readline()
      if args.verbose:
        print "<- %s" % response,
      if args.store_file:
        store.write(response)
    except serial.SerialTimeoutException:
      print "timeout %d secs on read" % timeout
      finish()
  return

def readFile(args):
  try:
    gcode = open( args.file)
  except:
    print "bad file"
    exit(1)
  gcodes = gcode.readlines()
  return gcodes

def initRobot(args):
  try:
    serialp=serial.Serial()
    serialp.port=args.serialport
    serialp.timeout=args.timeout
    serialp.baudrate=args.baud
    serialp.open()
  except IOError:
    print "robot not connected?"
    exit(1)
#  tty.setraw(serial);

  if args.home:
    serialp.write("c")
    readResponse(args,serialp,0)

  if args.setup_robot:
    print "speed and pwm"
    #speed and pwm
    serialp.write("p%d,%d" % (args.speed, args.pwm ))
    readResponse(args,serialp)
    #ms
    #none
    if args.ms == 0:
      MS0 = 0
      MS1 = 0
    #half
    elif args.ms == 1:
      MS0 = 1
      MS1 = 0
    #quarter
    elif args.ms == 2:
      MS0 = 0
      MS1 = 1
    #eigth
    elif args.ms == 3:
      MS0 = 1
      MS1 = 1
    print "microstep: %d, %d" % (MS0, MS1 )
    serialp.write("i%d,%d" % (MS0, MS1 ))
    readResponse(args,serialp)
    #where are we
    print "where are we?"
    serialp.write("q")
    readResponse(args,serialp)

  return serialp

def writeToRobot(args,serial,gcodes):
  p = re.compile( "^#" )
  for line in gcodes:
    if p.match(line):
      print "skipping line:", line
    elif not line == None:
      print "-> %s" % line,
      if not args.norobot:
        serial.write(line)
        readResponse(args,serial)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="feed polar files to polargraph robot")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--command', action='store', dest='command', help="command to send")
    group.add_argument('--file', action='store', dest='file', help="file to open")
    group.add_argument('--server', action='store', dest='server', help="server to check")

    parser.add_argument('--baud',
        action='store', dest='baud', type=int, default='57600',
        help="baud rate")
    parser.add_argument('--serialport',
        action='store', dest='serialport', default='/dev/ttyACM0',
        help="serial port to listen on")
    parser.add_argument('--store',
        action='store', dest='store_file', 
        help="file to write robot responses in")
    parser.add_argument('--verbose',
        action='store_const', const=True, dest='verbose', default=False,
        help="verbose")
    parser.add_argument('--norobot',
        action='store_const', const=True, dest='norobot', default=False,
        help="no robot connected, for testing")
    parser.add_argument('--home',
        action='store_const', const=True, dest='home', default=False,
        help="home to start")
    parser.add_argument('--setup_robot',
        action='store_const', const=True, dest='setup_robot', default=False,
        help="send pwm, ms etc commands to robot before the given file")
    parser.add_argument('--pwm',
        action='store', dest='pwm', type=int, default=80,
        help="pwm to draw")
    parser.add_argument('--speed',
        action='store', dest='speed', type=int, default=4,
        help="speed to draw")
    parser.add_argument('--serial-timeout',
        action='store', dest='timeout', type=int, default=1,
        help="timeout on serial read")
    parser.add_argument('--ms',
        action='store', dest='ms', type=int, default=0,
        help="micro step: 0,1,2,3")

    args = parser.parse_args()

    if args.store_file:
      store=open(args.store_file,'w+')

    #send a file   
    if args.file:
        gcodes = readFile(args)
    #send a command
    if args.command:
        gcodes=[args.command+"\n"]
    #use a remote server 
    if args.server:
        gcodes = fetch_data(args)

    if not gcodes:
        print >>sys.stderr, "no gcodes found"
        exit(1)

    if not args.norobot:
        serial = initRobot(args)
        writeToRobot(args,serial,gcodes)
        finish_serial()
