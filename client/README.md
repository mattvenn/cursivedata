# Feed

The feed.py program allows you to send commands to and query the robot.

# Examples

## Querying the robot

    ./feed.py --verbose --command q

## Calibrate the robot

    ./feed.py --verbose --command c

The robot should move the gondola to the top, then the top left, finally the top right. You should hear a click at the corners. Finally the gondola should move to the center of the drawing board.

## Force calibrate the robot, with string lengths of 100mm each

    ./feed.py --verbose --command f100,100

You might want to do this if you want to move the motors about without bothering to calibrate.

## Pen down

    ./feed.py --verbose --command d1

## Pen up

    ./feed.py --verbose --command d0

## Move a motor

unwind the left motor by 100 steps (not mm!):

    ./feed.py --command m100,0

wind in both motors by 200 steps:

    ./feed.py --command m-200,-200

# Dump config

    ./feed.py --dump-config

Will dump all your config to the screen and to a file called `config`. Useful for checking your parameters and finding your robot's ID.

# Update a single item of config

    ./feed.py --update-config id=8

Would set the id to 8.

# Setup with crontab

This is what I have in my crontab:

    */10 * * * * cd /home/pi/cursivedata/client/ ; ./feed.py --verbose --server --send-status >> log 2>&1

# Python Requirements

* argparse
* requests
* serial
