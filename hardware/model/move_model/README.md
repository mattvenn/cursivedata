# measuring velocity

http://www.embeddedrelated.com/showarticle/158.php

tldr:

The velocity resolution, for code that uses calculates Δpos/Δt using constant Δt, is 1/Δt.

If I were using the basic approach for estimating angular velocity, I would take the position estimates made at the primary control loop rate, take differences between successive samples, divide by Δt, and low-pass-filter the result with a time constant τ that reduces the bandwidth and error to the minimum acceptible possible. (A 1-pole or 2-pole IIR filter should suffice; if that kind of computation is expensive but memory is cheap, use a circular queue to store position of the last N samples and extend the effective Δt by a factor of N.)

# adaencoder

[interrupt speed](https://code.google.com/p/adaencoder/wiki/Speed)

83 microseconds corresponds to a frequency of 12 kilohertz.

[encoder I bought](http://www.ebay.co.uk/itm/171640123948) is 400 ppr (pulses
per rev), so 1600 cpr (counts per rev). So max speed is 7.5rps. 

# design spec

* max speed = 50cm/s
* max positional error = 2cm

From experiments with servo encoder and [this
article](http://static.micromo.com/media/wysiwyg/Technical-library/Encoders/Encoder_Feedback_Selection_WP.pdf)
I think I need 10 times number of counts than our error requirement. So
for 2cm accuracy I need 20 counts per cm of string.

At 50cm/s that is 1khz. Doubling for headroom I choose
2000khz, which easily fits in the 12khz bandwidth of adaencoder.

So to work out the size of the encoder wheel:

* the encoder gives 1600 cpr.
* need 20 sp cm
* need 80cm in a rev
* rev = 2 * pi * r
* r = 80/2 * pi = 12.73cm

That feels a bit unwieldy, so what happens if I say 5cm radius:

* 5cm radius = 31.4cm in a rev
* 1600 / 31.4 = 51 counts per cm

Top speed of 50cm/s is 2500khz. Which still fits in 12khz bandwidth fine.

# velocity sampling frequency (and PID loop frequency)

Not sure how to work this out. 

At low speeds error will be highest. At 1cm/s, with a 5cm radius encoder wheel,
I'll get 50 pulses per second. Sampling at:

* 10hz, velocity res = 1/dT = 10, 5 pulses counted

From pdf linked above, at a sample rate of 1khz, a required accuracy rps = 1000
/ (4 * cpr).

So at 1hz sampling, this would be rps = 1 / (4 * cpr). I understand this to mean
that if I want to be accurate to 1rps at 1hz, I need an encoder with 0.25 cpr. O
with 1cpr I can get accuracy of 4rps at 1hz.

So with
my encoder rps accuracy is 0.156. with a 5cm radius wheel this gives 4.84cm/s
speed accuracy (which means what?). At a sampling rate of 10hz, accuracy will be
100 x greater or 0.05cm/s.

The model I'm working on suggested 5cm lengths to divide long moves into.
In my design, speed errors will result in drawing errors. With worst error:
moving at 1.05cm/s, 5cm covered in 5.25s instead of 5s. Other servo is moving at
0.95cm/s so 5cm covered in 4.75s. 0.5s between servos finishing results in 0.5cm
error.

As this is a linear relationship, maximum sampling frequency to stay with 2cm
error is 4x = 40hz.

If error is too much, I can get more pulses by using a smaller encoding wheel.
Bandwidth suggests I can double again if necessary.

Previous PID test for the servo I made used 200hz sampling.

# Motor spec

[DC 12v motor](http://www.ebay.co.uk/itm/141742397705) is 120RPM at 12v.

* 120 RPM = 2 rps
* To get 50cm per second, need 25cm per rotation
* r = 25cm / 2 * pi = 3.98 cm radius.

[42rpm at
24v](http://uk.rs-online.com/web/p/products/440341/?cm_mmc=UK-PPC-_-google-_-3_RS_stock_codes-_-RS%7CPSF_421229%7CDC+Geared+Motors&mkwid=swEylgSmw_dc%7Cpcrid%7C83737117843%7Cpkw%7C440-341%7Cpmt%7Cp%7Cprd%7C&gclid=CM2drabqpMkCFYXNcgodqnoPTQ)

* torque 60 N-cm = 6.1 kg-cm. So can do 1kg with a 6cm radius.
* 42rpm = 0.7 rps
* r = 2 * Pi * 6 = 37cm circumference
* therefore 26cm per second.

[cpc]()

* torque 0.58N-m = 6kg-cm. Can do 1kg with 6cm radius
* 160 RPM = 2.6 rps
* r = 37cm
* 96cm / sec


# Testing

* 5cm r encoder wheels
* 4cm r motor drive wheels
* 20hz PID loop and velocity sampling

# Notes from Jon

* servos don't need a minimum speed
* use end spd and end pos as aims, allow servo control loop to solve problem
* buffer timestamped pos&spd data, then trigger that with controller time stamps
* encoder peripherals exist for higher b/w
* control loop should be running 10x faster than the movement bandwidth (do an fft of the position vs time graph of each servo)
* each servo controller will have 2 errors, pos and vel. So basic PID won't suffice.

# Notes from Joe

* 2upu controlloer
* inner outer loop cascade controllers
* differentiate kinematic equations to get velocity of a and b from xy
