# Welcome!

# Robot setup

## Warnings

* It's important to keep the strings tight or they will unravel on the spindles. This will badly affect the robot's ability to draw, and can jam and ruin the wires.
* Hang level and straight. Ideally against a flat wall.
* Take care not to pull down on the cables as the connectors are perpendicular to the floor and pulling the cables can damage the USB connector.
* Remove paper holding magnets and paper before calibrating/homing the machine.

## Gondola

* Untape the connector (at the V of the wires). There are 2 small hanger loops either side of the connector.
* Plug the connector into the gondola and attach the hanger loops onto the hooks on the servo mount.
* Keep the robot upright to ensure the gondola's weight keeps the wires taut.

## Wires

* Carefully remove all the tape from the front, the back and from around the motors and spindles.

## What to do if strings get loose

* After getting a USB connection and successfully using [feed.py](../client/README.md), use the motor command `m` to pay out enough wire to untangle it. Then wind up the wire while holding the wire taut, so that the spindle winds neatly.

## USB connection

* Linux: nothing required
* Mac: install drivers ? #TODO
* Windows: install drivers? #TODO

## Software

* download the [repository](http://github.com/mattvenn/cursivedata) 
* install the python library requirements detailed in [feed.py](../client/README.md)
* test by running ./feed.py

## Calibration

* Remove magnets and paper
* Run the calibration command using [feed.py](../client/README.md)

## Pen setup and testing

* Put some paper in and secure with the magnets
* Use feed.py to move the pen into the middle of the board (`g400,400` would work for an 800mm robot).
* Make sure the pen is up with `d0`
* Put a pen in the holder and tighten the bolt. Try to get the nib of the pen about 0.5mm away from the paper.
* Use `d1` to lower the pen, and make the gondola move with `g420,400`. Raise the pen with `d0` and you should have a 20mm long horizontal line. If not, try readjusting the pen.

## More information

There is also a [robot](robot.md) document that has more information about the robots and how they work/limitations.

# Internet/Website setup

## Create an endpoint

## Setup a data stream (name?)

## Configure a pipeline

## Raspberry Pi config

### Tips

I've found that while it's cool to have real time drawing, the noise of the robot can be annoying. I've started only doing drawing once an hour, or even just in the middle of the night. Use a crontab to set this up.

## crontab

see the [feed.py](../client/README.md) for info on crontabs


