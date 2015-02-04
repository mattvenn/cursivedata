# Robot Hardware Documentation

## Issues

* strings can unwind easily
* wobbly top lines
* a square isn't square

## Page limits

The robots can't draw over the whole back board because there are places where the strings are too tight (the top), or too loose (the sides). 

The middle good area is a square in the middle with a side length of approximately half the distance between the strings. So for the 800mm robots, about 400mm square.

The limits are in the robot's firmware but can be updated using the [feed](../client/README.md) command.

## Config

All the config (including page size, robot ID etc) are stored in the robot's firmware. This can be dumped, loaded or changed using the feed.py command.

## Robot defs?

* 0,0 is top left corner

## Robot safety

The robot will refuse to do anything until its calibrated. Though this can be overridden using the `f` command.


## Command definitions

* m100,100 : move motors manually. Winds both motor positive 100 steps. Makes strings longer. If steps per mm is 50, then both strings would be made longer by 2mm.
* q : query - get some information about where the robot is
* c : calibrate - home the strings
* g500,500 : move to x 500mm, y 500mm
* d0 : pen up
* d1 : pen down
