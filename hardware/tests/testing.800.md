# Acceptance Testing

This document outlines tests required before 800mm polarbots are shipped.

## Power

Supply 15V DC with a centre positive 2.2mm jack. 

Check that:

* Current drawn is less that 0.2A
* Power LED is on steady
* Status LED is flashing after a few seconds

## Software

Connect the polarbot to a suitable computer with a USB cable. Change into the ./client directory of the cursive data repository.

Check that:

* The robot appears as a serial port like /dev/ttyACM0
* The command `./feed.py --command q` runs and returns something like 'robot not calibrated'

## Basic functions

First force the robot's calibration with this command:

    ./feed.py --command f400,400

### Motor movement

Check both motors work with this command:

    ./feed.py --command m100,100

### Gondola raise and lower

These commands raise and lower the gondola's pen:

    ./feed.py --command d0
    ./feed.py --command d1

### Homing

This homes the polarbot:

    ./feed.py --command c

For a burn test, use this loop:

    while true; do ./feed.py --command c ; done

And leave running for 2 hours.

Check that:

* The gondola ends up in the middle of the board 
* The spindles stay tightly wound

## Drawing

Test the robot's drawing ability by drawing the test pattern:

    ./feed.py --file ../resources/svgtests/testpattern.800.polar

For a burn test, use this loop:

    while true; do ./feed.py --file ../resources/svgtests/testpattern.800.polar; done

And leave running for 2 hours.

Check that:

* The drawing's quality is 'good enough'
* The pen lifts and lowers correctly
* The outside square is within 5mm of being square
* The outside lines are straight within 1mm

# Final configuration

## Set ID

Each robot must have a unique ID the IDs should also be marked on the back of the robot.
Set an ID like this:

    ./feed.py --update-config id=10

The 4 new robots should have IDs 10,11,12,13.
