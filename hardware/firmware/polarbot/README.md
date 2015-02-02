# how the drawing works

responds only to 2 draw commands:

* d0 or d1 to raise or lower pen
* gX,Y to go to X,Y

# gX,Y

calls drawLine with mm arguments converted to steps:

    drawLine(p->arg1*config.stepsPerMM,p->arg2*config.stepsPerMM);

## drawLine()

* validates arguments lie in drawable area
* works out 2 control points cx and cy that lie between where pen is and destination
* calls drawCurve:


    drawCurve( x1, y1, fx, fy, cx, cy );

## drawCurve()

Draw a Quadratic Bezier curve from (x, y) to (fx, fy) using control pts (cx, cy)

* calculates up to 400 positions along the line
* if a position is far enough (more than 1 step) in either x or y, call moveTo

## moveTo()

* calculates the new string lengths. 
* Chooses to wind either motor forwards or backwards.
* while the string lengths are not equal to desired length moves the motors
* update new x and y position

# issues

* too many variable types. Should stick to floats or unsigned longs
* switching between mm and steps in the wrong place, so numbers get too big
* too many needless calculations (in drawCurve and moveTo)
* no need for a quadratic bezier - we only use straight lines
* drawCurve does 400 calcs regardless of line length
