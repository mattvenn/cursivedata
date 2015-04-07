#!/usr/bin/python
""" 
utility program to get min and max moves from the file
"""
import sys
if len(sys.argv) != 2:
    print("filename argument required")
    exit(1)
lines = open(sys.argv[1]).readlines()
import re
minx = 10000
maxx=0
miny=10000
maxy=0
for line in lines:
  m=re.search('g(\S+),(\S+)',line)
  if m:
    x= float(m.group(1))
    y= float(m.group(2))
#    print "x", x, "y", y
    if y > maxy:
      maxy=y
    if y < miny:
      miny=y
    if x > maxx:
      maxx=x
    if x < minx:
      minx=x

print("min/max x: %d %d" % (minx,maxx))
print("min/max y: %d %d" % (miny,maxy))
print("commands:")
print("g%d,%d" % (minx,miny))
print("g%d,%d" % (maxx,miny))
print("g%d,%d" % (maxx,maxy))
print("g%d,%d" % (minx,maxy))
print("g%d,%d" % (minx,miny))
