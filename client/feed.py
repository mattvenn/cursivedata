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
import datetime
import string
import argparse
import signal
import socket
import serial

def send_status(status):
    print "sending status to server"
    data = urllib.urlencode(status)
    url = args.server + "/status?" + data
    try:
        response = urllib2.urlopen(url)
        the_page = response.read()
        print the_page
    except urllib2.URLError, e:
        print e.code
        print e.read()

def fetch_data():
    if args.verbose:
        print "fetching from ", args.server
    req = urllib2.Request(args.server)
    try:
        response = urllib2.urlopen(req)
        gcodes = response.read()
        if args.verbose:
            print "got answer from server:"
            print gcodes
        return gcodes.splitlines()
    except urllib2.URLError, e:
        print >>sys.stderr, e.code
        print >>sys.stderr, e.read()
        return None


def finish_serial():
  if serial_port:
      print "closing serial"
      print serial_port
      serial_port.close()

"""
this requires the robot to respond in the expected way, where all responsed end with "ok"
"""
def read_serial_response():

  response = ""
  all_lines = ""
  while string.find(response,"ok"):
    try:
      response = serial_port.readline()
      if args.verbose:
        print "<- %s" % response,
      all_lines += response
    except serial.SerialTimeoutException:
      print "timeout %d secs on read" % args.timeout
      finish()
  return all_lines

def readFile():
  try:
    gcode = open(args.file)
  except:
    print "bad file"
    exit(1)
  gcodes = gcode.readlines()
  return gcodes

def setup_serial():
  try:
    serial_port=serial.Serial()
    serial_port.port=args.serialport
    serial_port.timeout=args.timeout
    serial_port.baudrate=args.baud
    serial_port.open()
  except IOError:
    print "robot not connected?"
    exit(1)
#  tty.setraw(serial);
  return serial_port

def setup_robot():
    #microstepping arguments
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

    setup_commands= [
            #speed and pwm
            "p%d,%d" % (args.speed, args.pwm ),
            "i%d,%d" % (MS0, MS1 ),
        ]
    #home
    if args.home:
        setup_commands.append("c")
    
    send_robot_commands(setup_commands)


def send_robot_commands(gcodes):
  p = re.compile( "^#" )
  response = ""
  for line in gcodes:
    if p.match(line):
      print "skipping line:", line
    elif not line == None:
      print "-> %s" % line,
      serial_port.write(line)
      response += read_serial_response()
  return response

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
    parser.add_argument('--send-status',
        action='store_const', const=True, dest='sendstatus', default=False,
        help="send current status of the robot to the server")
    parser.add_argument('--no-robot',
        action='store_const', const=True, dest='norobot', default=False,
        help="no robot connected, for testing")
    parser.add_argument('--home',
        action='store_const', const=True, dest='home', default=False,
        help="home to start")
    parser.add_argument('--setup-robot',
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


    #send a file   
    if args.file:
        gcodes = readFile()
    #send a command
    if args.command:
        gcodes=[args.command+"\n"]
    #use a remote server 
    if args.server:
        gcodes = fetch_data()

    if args.sendstatus and args.server and not args.norobot:
        serial_port = setup_serial()
        status_commands=["q\n"]
        response = send_robot_commands(status_commands)
        finish_serial()
        status = {
            "run time" : str(datetime.datetime.now()),
            "q" : response,
            }
        send_status(status)

    if not gcodes:
        print >>sys.stderr, "no gcodes found"
        exit(1)

    if not args.norobot:
        time.sleep(1)
        serial_port = setup_serial()
        if args.setup_robot:
            setup_robot()
        response = send_robot_commands(gcodes)
        if args.store_file:
          store=open(args.store_file,'w+')
          store.write(response)
        finish_serial()

