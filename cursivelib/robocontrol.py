#!/usr/bin/python
"""
I've pulled this wholesale out of feed.py, and just started updating the 
immediately necessary bits. Don't trust *anything* below the big comment...

main problem with reading and writing to the robot is that if we read too much we hang.
if we don't read enough, the leonardo resets!
"""
#import parse_header
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

class RobotController:

    def __init__(self,port="/dev/ttyACM0",verbose=True,timeout=120,baud=57600,):
        print("init")
        self.port = port
        self.verbose = verbose
        self.timeout = timeout
        self.baud=baud

    def setup_serial(self):
      try:
	print "Starting serial on ",self.port
        serial_port=serial.Serial()
        serial_port.port=self.port
        serial_port.timeout=self.timeout
        serial_port.writeTimeout = self.timeout
        serial_port.baudrate=self.baud
        serial_port.open()
        self.serial_port = serial_port
      except IOError, e:
        print "robot not connected?", e
      return serial_port


    def finish_serial(self):
        try:
            if self.verbose:
                print "closing serial"
            self.serial_port.close()
        except serial.SerialException:
            # We are explicitely silencing the error here.
            # TODO: Log the error message at least.
            pass

    """
    this requires the robot to respond in the expected way, where all responsed end with "ok"
    """
    def read_serial_response(self):
      response = ""
      all_lines = ""
      #this needs to find a \r\nok\r\n I think, but don't know why
      #just ok\r\n doesn't work
      while string.find(response,"ok"):
        response = self.serial_port.readline()
        if response == "":
          print >>sys.stderr, "timeout on serial read"
          self.finish_serial()
          exit(1)
        if self.verbose:
          print "<- %s" % response,
        all_lines += response
      return all_lines

    def send_robot_commands(self,gcodes):
      p = re.compile( "^#" )
      response = ""
      for line in gcodes:
        if p.match(line):
          print "skipping line:", line
        elif not line == None:
          if self.verbose:
            print "-> %s" % line,
          self.serial_port.write(str(line)) #str added because we get unicode from the server
          response += self.read_serial_response()
      return response

############################################################
#
# Stuff below here hasn't been updated
#
############################################################



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
                elif r.status_code == 204:
                    #end of the gcodes
                    return gcodes
                elif r.status_code == 404:
                    print("server has a problem with the gcodes")
                    print("try refreshing URL by hand to clear bad gcode files")
                else:
                    print "unexpected server response ", r.status_code 
                    return None

            except requests.exceptions.ConnectionError, e:
                print >>sys.stderr, e
                return None





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


    def dump_config():
            (pack,names,values) =  get_robot_config()
            config = {}
            for i in range(len(names)):
              print names[i], '=', values[i]
              config[names[i]] = values[i]
            print("config dumped to file: config")
            open("config",'w').write(json.dumps(config))








