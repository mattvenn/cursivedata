#!/usr/bin/python
import socket
import sys
import signal
import json

portnum = int(sys.argv[1])

def signal_handler(signum, frame):
    print "closing socket"
    global sock
    sock.close()
    exit(1)

signal.signal(signal.SIGINT, signal_handler)


def extractData(line):
    jsondata = urllib.unquote(line)
    trigger = json.loads(jsondata.lstrip("body="))
    light = trigger["triggering_datastream"]["value"]["value"]
    time = trigger["triggering_datastream"]["at"]
    print "got %s at %s" % ( light, time )
    return (light,time)

def processData((light,time)):
    import iso8601
    date = iso8601.parse_date(time)
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    mins =  (minute + hour * 60)/10 # 0 - 143
    seconds = date.strftime("%s")
    print seconds

    import subprocess
    print >>sys.stderr, "building squares"
    subprocess.call(["./squares.py", "--number", str(mins), "--env", str(int(float(light)))])
    import os
    if os.path.isfile("squares.svg"):
        print >>sys.stderr, "new robot data"
        #run the pycam stuff here
        #move the file to history with a timestamp
        newfile = "./history/" + str(seconds) + ".svg" 
        os.rename("squares.svg", newfile)
        subprocess.call("./concat.py")

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server_address = ('mattvenn.net', portnum)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print >>sys.stderr, '-----------------'
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()

    try:
        print >>sys.stderr, 'connection from', client_address

        # Receive the data in small chunks and retransmit it
        import urllib
        while True:
            try:
                data = connection.recv(4096)
                if data:
                    for line in data.split("\n"):
                        if line.startswith("body="):
                            processData( extractData(line) )
			    break

                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
            except:
                e = sys.exc_info()[0]
                print e
                connection.close()
                sock.close()
                exit(1)
            
    finally:
        # Clean up the connection
        connection.close()
