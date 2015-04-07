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

## Power

* Plug the power supply (15Vdc, center positive)
* You should see the red power LED come on and stay on
* You should also see a flashing red status LED
* You should hear the gondola's servo lift move 

## USB connection

Linux and Mac need no drivers. If you are using Windows, see this [Arduino document on Leonardo drivers](http://arduino.cc/en/Guide/ArduinoLeonardoMicro?from=Guide.ArduinoLeonardo#toc8). 

## Software

* download the [repository](http://github.com/mattvenn/cursivedata) 
* install the python library requirements detailed in [feed.py](../client/README.md)
* test by running `./feed.py --command q`. You may need to specify a different serial portusing `--serialport`. The default is `/dev/ttyACM0`

## Calibration

* Remove magnets and paper
* Run the calibration command using [feed.py](../client/README.md)

## More information

There is also a [robot](robot.md) document that has more information about the robots and how they work/limitations.

# Internet/Website setup

For most of this you will need to be logged in on the website. Contact me for a password.

## Create an endpoint

Each robot needs its own endpoint. Go to [create endpoint](http://cursivedata.co.uk/endpoint/create)

Fill in the details and click `create`. The website will take you to a new page for your robot. Make a note of the ID, which is the number after `endpoint` in the URL.

## Change your robot's ID

If your robot's ID was 8, use this command to set the robot's new ID:

    ./feed.py --update-config id=8

## Update the website with your robot's details

    ./feed.py --update-dimensions

Then reload the endpoint page and check that the dimensions have changed and you now have a green tick instead of a red cross.

## Draw something!

First, turn on gcode output by clicking the `Start Gcode` button.

We recommend trying first with no paper or pen.

You can draw SVGs by using the `upload SVG` tool on the endpoint page. Choose 5x5squares.svg from the [resources directory](../resources/svgtests). Choose a width (in mm) that will fit in your robot, then click the `upload SVG` button.

After a moment the page will be updated and in the top section you will see that there is a file to serve with a link to the gcodes. You will also see your picture shown on the `latest visualations` section of the page.

Get the robot to draw the picture by running the feed command:

    ./feed.py --verbose --server

The svg generation will place the picture at the top centre of the robot's drawing area.

## Pen setup and testing

* Put some paper in and secure with the magnets
* Put a pen in the holder and tighten the bolt. Try to get the nib of the pen about 0.5mm away from the paper.
* Run the above test again and check the robot is drawing well.

## Setup a pipeline

This is the part of the website that takes external data, processes it with a pattern generator and delivers it to an endpoint. You can find more about the [structure of the website here](https://github.com/mattvenn/cursivedata/wiki/overview).

First, [create a new pipeline](http://cursivedata.co.uk/pipeline/create). Choose your source, generator and endpoint. You can change the image width and height later. Press the `submit` button and you'll be redirected to the new pipeline's page.

Here's a summary of the parameters on the page:

### Controls

* Auto begin days: automatically 'presses the begin button' every X days.
* Reset: reset the data and image
* Begin: some generators will draw a start title when beginning
* End: some generators will draw an end title when ending
* Pause: pause

### Page size and offset

For moving the drawing around the page. Useful if you want a few pipelines drawing on one endpoint.

### Generator parameters

For changing the various parameters of the drawing algorithms.

### Current drawing and latest drawings

Shows the current and most recent drawings (though often needs a refresh)

## Setup a data source

* Create a new feed on xively and check it's working
* [Create a new data source on cursive data](http://cursivedata.co.uk/sources/create)
* Change the name to a useful name
* Change the feed id to your xively feed's id
* Change the stream id to the channel name of the specific data set you want.
* Click `create`, which will take you the new data source page. You will see a graph of the last day's data.
* Click the `enable` button to start the data source working.

## Raspberry Pi config

### Tips

I've found that while it's cool to have real time drawing, the noise of the robot can be annoying. I've started only doing drawing once an hour, or even just in the middle of the night. Use a crontab to set this up.

## crontab

see the [feed.py](../client/README.md) for info on crontabs


