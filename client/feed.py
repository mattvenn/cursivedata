#!/usr/bin/python
"""
main problem with reading and writing to the robot is that if we read too much we hang.
if we don't read enough, the leonardo resets!
"""
import parse_header
import struct
import sys
import json
import re
import sys
import time
import fcntl
import datetime
import string
import argparse
import signal
import serial
import requests

class FeedParseError(Exception):
    pass


#queries the robot for all its config
def get_robot_config():
    status_commands=["j"]
    response = send_robot_commands(status_commands)
    try:
      m=re.match('(.*)\r\nok\r\n',response,re.S)
      string = m.group(1)

    except AttributeError:
      print "couldn't parse robot's output:", response
      return

    #load this from the config file
    (names,pack) = parse_header.parse_header()
    fmt = "=" + ''.join(pack)
    try:
      values = struct.unpack(fmt,string)
      return (pack,names,list(values))
    except struct.error:
      print "bad data, machine said:", response
      exit(1)

#takes a json config file and loads into the robot
def load_robot_config():
    config = json.load(open(args.loadconfig)) 
    #check the config is ok
    (pack,names,values) = get_robot_config()
    for key in config.keys():
        try:
            values[names.index(key)] = config[key]
        except ValueError:
            print key, "not in robot's config"
            exit(1)
    #otherwise, ok to go
    load_config(pack,values)

#loads config into the robot
def load_config(pack,values):
    fmt = "=" + ''.join(pack)
    string = struct.pack(fmt,*values) 
    response = send_robot_commands(["k0,0"])
    #don't use the function we have, as it doesn't work with this - because of line splitting?
    serial_port.write(string) 
    print read_serial_response()

#update a single value of the robots config. Checks against the robot's config.h
def update_robot_config():
    print args.updateconfig
    (pack,names,values) = get_robot_config()
    m = re.match('(\w+)=(\w+)',args.updateconfig)
    if m:
      if m.group(1) in names:
        try:
          value = float(m.group(2))
          values[names.index(m.group(1))] = value
          load_config(pack,values)
        except ValueError:
          print "bad value", m.group(2)
        
      else:
        print "no such name", m.group(1)
        print "use one of", names
       
    else:
      print "didn't understand config, needs to be name=value", args.updateconfig

#fetches robot id
def fetch_robot_id():
    if args.norobot:
        return "1"

    (pack,names,values) = get_robot_config()
    index = names.index("id")
    return str(values[index])

def update_robot_dimensions():
    status_commands=["u"]
    response = send_robot_commands(status_commands)
    try:
      m=re.search('^top margin: ([0-9.]+)',response,re.M)
      top_margin=m.group(1)
      m=re.search('^side margin: ([0-9.]+)',response,re.M)
      side_margin=m.group(1)
      m=re.search('^h: ([0-9.]+)',response,re.M)
      height=m.group(1)
      m=re.search('^w: ([0-9.]+)',response,re.M)
      width=m.group(1)
    except AttributeError:
      raise FeedParseError("couldn't parse robot's output:%s" % response)

    payload = {
        'width': float(width),
        "height": float(height),
        "side_margin": float(side_margin) + 5, #hack, robot should return larger than needed
        "top_margin": float(top_margin) + 5, #hack, robot should be  ypdated
        }

    url = args.url + '/api/v1/endpoint/' + fetch_robot_id() + "/"
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
    if not args.norobot:
        response = send_robot_commands(status_commands)
    else:
        response = "pretend robot response"

    payload = {
        'status': response,
        }

    url = args.url + '/api/v1/endpoint/' + fetch_robot_id() + "/"
    headers = {'content-type': 'application/json'}
    r = requests.patch(url, data=json.dumps(payload),headers=headers)
    print r.status_code
    if r.status_code == 202:
        print "updated ok"
    else:
        print "failed to update"
    return response
    
def fetch_data():
    url = args.url + '/endpoint_data/' + fetch_robot_id() + "/?consume=true"
    if args.verbose:
        print "fetching from", url
    gcodes = []
    count = 0
    while True:
        count += 1
        try:
            r = requests.get(url)
            if r.status_code == 200:
                new_codes = r.text.splitlines()
                if args.verbose:
                    print "%d: got %d gcodes from server" % ( count, len(new_codes) )
                gcodes = gcodes + new_codes
            elif r.status_code == 404:
                #end of the gcodes
                return gcodes
            else:
                print "unexpected server response ", r.status_code 
                return None

        except requests.exceptions.ConnectionError, e:
            print >>sys.stderr, e
            return None


def finish_serial():
    try:
        if args.verbose:
            print "closing serial"
        serial_port.close()
    except serial.SerialException:
        # We are explicitely silencing the error here.
        # TODO: Log the error message at least.
        pass

"""
this requires the robot to respond in the expected way, where all responsed end with "ok"
"""
def read_serial_response():

  response = ""
  all_lines = ""
  #this needs to find a \r\nok\r\n I think, but don't know why
  #just ok\r\n doesn't work
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
  gcode = open(args.file)
  gcodes = gcode.readlines()
  return gcodes

def setup_serial():
  try:
    serial_port=serial.Serial()
    serial_port.port=args.serialport
    serial_port.timeout=args.timeout
    serial_port.writeTimeout = args.timeout
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
      if args.verbose:
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
    group.add_argument('--update-config',
        action='store', dest='updateconfig',
        help="update one element of the robot's config")
    group.add_argument('--load-config',
        action='store', dest='loadconfig', 
        help="load a json config into the robot")
    group.add_argument('--dump-config',
        action='store_const', dest='dumpconfig', const=True, default=False,
        help="dump the robot's config")

    parser.add_argument('--baud',
        action='store', dest='baud', type=int, default='57600',
        help="baud rate")
    parser.add_argument('--serialport',
        action='store', dest='serialport', default='/dev/ttyACM0',
        help="serial port to listen on")
    parser.add_argument('--url',
        action='store', dest='url', default='http://cursivedata.co.uk',
        help="url of the server")
    parser.add_argument('--store',
        action='store', dest='store_file', 
        help="file to write robot responses in")
    parser.add_argument('--verbose',
        action='store_const', const=True, dest='verbose', default=True,
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
        action='store', dest='timeout', type=int, default=120,
        help="timeout on serial read")
    parser.add_argument('--ms',
        action='store', dest='ms', type=int, default=0,
        help="micro step: 0,1,2,3")

    args = parser.parse_args()

    print "started ", datetime.datetime.now()
    gcodes = []

    #locking
    file = "/tmp/feed.lock"
    fd = open(file,'w')
    try:
        print "check lock"
        fcntl.lockf(fd,fcntl.LOCK_EX | fcntl.LOCK_NB)
        print "ok"
    except IOError:
        print "another process is running with lock. quitting!", file
        exit(1)

    #get serial init first, as lots depends on getting data from the robot
    if args.norobot:
        update_robot_status()
        exit(0)
    else:
        serial_port = setup_serial()
        if args.updatedimensions:
            update_robot_dimensions()
	#we should check robot's status anyway, regardless of sending it to server
        if args.sendstatus:
            response = update_robot_status()


    #send a file   
    if args.file:
        gcodes = readFile()
    #send a command
    if args.command:
        gcodes=[args.command]
    #use a remote server 
    if args.server:
        gcodes = fetch_data()


    if args.dumpconfig:
        (pack,names,values) =  get_robot_config()
        config = {}
        for i in range(len(names)):
          print names[i], '=', values[i]
          config[names[i]] = values[i]
        open("config",'w').write(json.dumps(config))
    if args.updateconfig:
        update_robot_config()
    if args.loadconfig:
        load_robot_config()

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


