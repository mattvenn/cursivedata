""" 
utility program to get min and max moves from the file
"""
lines = open("text.polar").readlines()
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
    print "x", x, "y", y
    if y > maxy:
      maxy=y
    if y < miny:
      miny=y
    if x > maxx:
      maxx=x
    if x < minx:
      minx=x

print minx,maxx,miny,maxy
