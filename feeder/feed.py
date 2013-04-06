#!/usr/bin/python
import re
import sys
import tty
import time
import string
import argparse
import signal
import socket

TIMEOUT = 0.5 # number of seconds your want for timeout

def handler():
  print "timed out on serial read"

def signal_handler(signum, frame):
    print "closing socket"
    global sock
    sock.close()
    exit(1)

signal.signal(signal.SIGALRM, handler)
signal.signal(signal.SIGINT, signal_handler)

"""
this requires the robot to respond in the expected way, where all responsed end with "ok"
"""
def readResponse(args,serial,timeout=10):
  response = ""
  #print "setting timeout to", timeout
  while string.find(response,"ok"):
    try:
      if(timeout > 0):
        signal.alarm(timeout)
      response = serial.readline()
      signal.alarm(0)
      if args.verbose:
        print "<", response,
    except SerialTimeoutException:
      print "timeout %d secs on read" % timeout
      return

def readFile(args):
  gcode = open( args.file)
  gcodes = gcode.readlines()
  return gcodes

def initRobot(args):
  serial = None
  port = args.serialport
  try:
    serial = open( port, 'r+' )
  except IOError:
    print "robot not connected?"
    exit(1)
  tty.setraw(serial);

  if args.home:
    serial.write("c")
    readResponse(args,serial,0)

  print "speed and pwm"
  #speed and pwm
  serial.write("p%d,%d" % (args.speed, args.pwm ))
  readResponse(args,serial)
  #ms
  print "microstep: %d, %d" % (MS0, MS1 )
  serial.write("i%d,%d" % (MS0, MS1 ))
  readResponse(args,serial)
  #where are we
  print "where are we?"
  serial.write("q")
  readResponse(args,serial)

  return serial

def writeToRobot(args,serial,gcodes):
  p = re.compile( "^#" )
  for line in gcodes:
    if p.match(line):
      print "skipping line:", line
    elif not line == None:
      print "> %s" % line
      if not args.norobot:
        serial.write(line)
        readResponse(args,serial)

def setupPort(args):
  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  # Bind the socket to the port
  server_address = ('localhost', args.port)
  print >>sys.stderr, 'starting up on %s port %s' % server_address
  sock.bind(server_address)
  # Listen for incoming connections
  sock.listen(1)
  return sock

def listenPort(args,serial,sock):
  while True:
      # Wait for a connection
      print >>sys.stderr, '-----------------'
      print >>sys.stderr, 'waiting for a connection'
      connection, client_address = sock.accept()

      try:
          print >>sys.stderr, 'connection from', client_address
          while True:
              data = connection.recv(4096)
              if data:
                  gcodes = data.split("\n")
                  writeToRobot(args,serial,gcodes)
              else:
                  print >>sys.stderr, 'no more data from', client_address
                  break
      finally:
          # Clean up the connection
          connection.close()
          sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="feed polar files to polargraph robot")
    parser.add_argument('--port',
        action='store', dest='port', type=int,
        help="port to listen on")
    parser.add_argument('--serialport',
        action='store', dest='serialport', default='/dev/ttyACM0',
        help="serial port to listen on")
    parser.add_argument('--file',
        action='store', dest='file', 
        help="file to open")
    parser.add_argument('--verbose',
        action='store_const', const=True, dest='verbose', default=False,
        help="verbose")
    parser.add_argument('--norobot',
        action='store_const', const=True, dest='norobot', default=False,
        help="no robot connected, for testing")
    parser.add_argument('--home',
        action='store_const', const=True, dest='home', default=False,
        help="home to start")
    parser.add_argument('--pwm',
        action='store', dest='pwm', type=int, default=80,
        help="pwm to draw")
    parser.add_argument('--speed',
        action='store', dest='speed', type=int, default=4,
        help="speed to draw")
    parser.add_argument('--ms',
        action='store', dest='ms', type=int, default=0,
        help="micro step: 0,1,2,3")


    args = parser.parse_args()
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

    if args.file:
      gcodes = readFile(args)
      if not args.norobot:
        serial = initRobot(args)
        writeToRobot(args,serial,gcodes)
      print "finished"
    elif args.port:
      sock = setupPort(args)
      if not args.norobot:
        serial = initRobot(args)
      else:
        serial = None
      listenPort(args,serial,sock)
    else:
      print "must specify either port or file"
      exit(1)

