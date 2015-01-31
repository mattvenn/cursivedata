# Modelling spindle radius

With the large drawbot, the spindle radius changes as the string wraps.
This results in distorted drawings.

Do we have to measure this or can we model it?

![plot](plot.png)

Short answer: maybe.

# Measurements

Using 2 spindle widths of 7 and 11mm, I recorded the rough splindle diameter into [7mm.csv](7mm.csv) and [11mm.csv](11mm.csv). The spindles were wound 32000 steps for each measurement (roughly one meter of string).

# Model

Then a [dirty python](model.py) script was used to make a model of how spindle diameter changes as a function of turns. This is used to create 2 new csv files.

# Plot

All 4 csv files are plotted using [plot.py](plot.py) which depends on matplotlib . 
Use [show.sh](show.sh) to create the modelled data and then plot all files on the same graph.

    ./show.sh

# Discussion

I messed with the fudge factor in the model which adjusts how well the string
packs. 1 is as perfect cylinders. At 1.9, the model for the thinner spindle
width (7mm) starts to match up pretty well. 

I assume the smaller the spindle width, the better we can model because the
string is forced to pile up more evenly.

Even if we did have some way to measure the spindle diameter, it still may not
be correct. Imagine the string is piled up more on one side than the other. Then
the string starts filling in the space. The diamter of the spindle will now be
smaller than measured.

A better way of measuring would be to have the string run round a dimensioned
spindle that creates a pulse every revolution or fraction of one. This can then
be used to know exactly how much string has been wound out.

# Conclusion

The model may well improve results, and especially on a large scale the small
errors wouldn't necessarily be a problem.

If more precision is required, the measuring spindles mentioned above could be
used.

Both methods require changes being made to the firmware of the motor controller,
but only the second method requires hardware changes.

Therefore, test the model on the robot first. Move to the measuring version if
still not accurate enough.
