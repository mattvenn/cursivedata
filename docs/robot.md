# Robot Hardware Documentation

## Issues

* strings can unwind easily
* wobbly top lines
* a square isn't square


## Page limits

* 

## Robot defs?

* 0,0 is top left corner


## Command definitions

* m100,100 : move motors manually. Winds both motor positive 100 steps. Makes strings longer. If steps per mm is 50, then both strings would be made longer by 2mm.
* q : query - get some information about where the robot is
* c : calibrate - home the strings
* g500,500 : move to x 500mm, y 500mm
* d0 : pen up
* d1 : pen down
