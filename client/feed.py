#!/usr/bin/python
"""
main problem with reading and writing to the robot is that if we read too much we hang.
if we don't read enough, the leonardo resets!
"""
import sys
import json
import re
import sys
import time
import datetime
import string
import argparse
import signal
import serial
import requests


def update_robot_dimensions():
    status_commands=["u"]
    response = send_robot_commands(status_commands)
    try:
      m=re.search('^top margin: ([0-9.]+)mm',response,re.M)
      top_margin=m.group(1)
      m=re.search('^side margin: ([0-9.]+)mm',response,re.M)
      side_margin=m.group(1)
      m=re.search('^h: ([0-9.]+)mm',response,re.M)
      height=m.group(1)
      m=re.search('^w: ([0-9.]+)mm',response,re.M)
      width=m.group(1)
    except:
      print "couldn't parse robot's output:", response
      return
      
    
    payload = {
        'width': width,
        "height": height,
        "side_margin": side_margin,
        "top_margin": top_margin,
        }

    url = args.apiurl + "endpoint/" + str(args.robot_id) + "/"
    headers = {'content-type': 'application/json'}
    r = requests.patch(url, data=json.dumps(payload),headers=headers)
    print r.status_code
    if r.status_code == 202:
        print "updated ok"
    else:
        print "failed to update"
        print r.text.replace("\\n","\n")

def update_robot_status():
    status_commands=["q"]
    response = send_robot_commands(status_commands)

    payload = {
        'url': response,
        }

    url = args.apiurl + "endpoint/" + str(args.robot_id) + "/"
    headers = {'content-type': 'application/json'}
    r = requests.patch(url, data=json.dumps(payload),headers=headers)
    print r.status_code
    if r.status_code == 202:
        print "updated ok"
    else:
        print "failed to update"

def fetch_data():
    url = args.endpointurl + str(args.robot_id) + "/?consume=true"
    if args.verbose:
      print "fetching from ", url
    try:
      r = requests.get(url)
      if r.status_code == 200:
        gcodes = r.text
        if args.verbose:
          print "got answer from server:"
          print gcodes
        return gcodes.splitlines()
      else:
        raise Exception( "failed with", r.status_code )

    except requests.exceptions.ConnectionError, e:
      print >>sys.stderr, e.code
      print >>sys.stderr, e.read()
      return None


def finish_serial():
  if serial_port:
      print "closing serial"
      #print serial_port
      serial_port.close()

"""
this requires the robot to respond in the expected way, where all responsed end with "ok"
"""
def read_serial_response():

  response = ""
  all_lines = ""
  while string.find(response,"ok"):
    response = serial_port.readline()
    if response == "":
      print >>sys.stderr, "timeout on serial read"
      finish_serial()
      exit(1)
    if args.verbose:
      print "<- %s" % response,
    all_lines += response
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
  except IOError, e:
    print "robot not connected?", e
    exit(1)
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
      serial_port.write(str(line)) #str added because we get unicode from the server
      response += read_serial_response()
  return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="feed polar files to polargraph robot")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--command', action='store', dest='command', help="command to send")
    group.add_argument('--file', action='store', dest='file', help="file to open")
    group.add_argument('--server', action='store_const', const="True", dest='server', help="fetch gcodes from server (set by apiurl and robotid)")
    group.add_argument('--log', action='store_const', const=True, dest='log', help="just print responses")
    group.add_argument('--update-dimensions',
        action='store_const', const=True, dest='updatedimensions', default=False,
        help="update the server with this robot's dimensions")

    parser.add_argument('--baud',
        action='store', dest='baud', type=int, default='57600',
        help="baud rate")
    parser.add_argument('--serialport',
        action='store', dest='serialport', default='/dev/ttyACM0',
        help="serial port to listen on")
    parser.add_argument('--endpointurl',
        action='store', dest='endpointurl', default='http://mattvenn.net:8080/polargraph/endpoint_data/',
        help="endpoint url, must end with /")
    parser.add_argument('--apiurl',
        action='store', dest='apiurl', default='http://mattvenn.net:8080/api/v1/',
        help="api url, must end in a /")
    parser.add_argument('--store',
        action='store', dest='store_file', 
        help="file to write robot responses in")
    parser.add_argument('--verbose',
        action='store_const', const=True, dest='verbose', default=False,
        help="verbose")
    parser.add_argument('--no-send-status',
        action='store_const', const=False, dest='sendstatus', default=True,
        help="don't send current status of the robot to the server")
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
    parser.add_argument('--robot-id',
        action='store', dest='robot_id', type=int, default=1,
        help="robot's endpoint id")
    parser.add_argument('--speed',
        action='store', dest='speed', type=int, default=4,
        help="speed to draw")
    parser.add_argument('--serial-timeout',
        action='store', dest='timeout', type=int, default=10,
        help="timeout on serial read")
    parser.add_argument('--ms',
        action='store', dest='ms', type=int, default=0,
        help="micro step: 0,1,2,3")

    args = parser.parse_args()
    gcodes = []

    #send a file   
    if args.file:
        gcodes = readFile()
    #send a command
    if args.command:
        gcodes=[args.command]
    #use a remote server 
    if args.server:
        gcodes = fetch_data()

    if not args.norobot:
        serial_port = setup_serial()
    if args.updatedimensions and not args.norobot:
        update_robot_dimensions()
    if args.sendstatus and not args.norobot:
        update_robot_status()

    if not args.norobot:
      if args.setup_robot:
        setup_robot()

    if len(gcodes):
      response = send_robot_commands(gcodes)
    elif args.log:
      while True:
        response = read_serial_response()
    else:
      print "no gcodes found"

    if args.store_file:
      store=open(args.store_file,'w+')
      store.write(response)

    finish_serial()


