#!/usr/bin/python
import serial, sys, os, time

def reset():
    ser = serial.Serial( 
        port=serialPort, baudrate=1200, 
        parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, 
        bytesize=serial.EIGHTBITS )
    ser.isOpen()
    ser.close() # always close port


def upload():
    hexFile = "leonardoTests.cpp.hex"
    os.system("avrdude -patmega32u4 -cavr109 -P%s -b57600 -D -Uflash:w:./%s:i" % (serialPort, hexFile))

if __name__ == '__main__':
    serialPort = sys.argv[1] #"/dev/ttyACM1"
    reset()
    time.sleep(2)
    upload()

