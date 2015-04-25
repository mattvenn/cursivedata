
import re
import argparse

import pysvg.structure
from cursivelib.robot_spec import *
from cursivelib.robot_spec import string_to_spec
from cursivelib.svg_to_gcode import *
from cursivelib.pycam_gcode import *
import cursivelib.svg as svg
import pysvg.text as txt


class GcodeToSVG :
    def __init__(self,robot,
            min_dwell=80,max_dwell=240,drill_size=50,dwell_fill="rgb(255,230,210)",
            pen_size=0.2,pen_color="rgb(255,100,100)",
            area_outline="rgb(200,200,150)", area_fill="rgb(255,255,240)",
            drawable_outline = "rgb(100, 255, 100)", drawable_fill="rgb(240,255,240)",
            drawing_outline = "rgb(128,128,128)", drawing_fill="rgb(240,255,240)",
            outline_size=0.5,
            font_size=20
            ):
        self.robot = robot
        self.min_dwell=min_dwell
        self.max_dwell=max_dwell
        self.dwell_fill=dwell_fill
        self.drill_size = drill_size

        self.pen_size = pen_size
        self.pen_color=pen_color

        self.area_outline=area_outline
        self.area_fill=area_fill
        self.drawable_outline=drawable_outline
        self.drawable_fill=drawable_fill
        self.drawing_outline=drawing_outline
        self.drawing_fill=drawing_fill

        self.outline_size = outline_size
        self.font_size = font_size

        self.moveCode = re.compile( "^g(.*),(.*)$")
        self.penCode = re.compile( "^d(.*)$")
        self.dwellCode = re.compile( "^v(.*)$")
        self.build = pysvg.builders.ShapeBuilder()




    def convert(self,infile,outfile) :
        self.doc = pysvg.structure.svg(width=self.robot.width,height=self.robot.height)
        self.draw_areas()
        self.draw_codes(infile)
        self.doc.save(outfile)

    def draw_areas(self) :
        # Whole area
        self.add_rect(self.doc,0, 0, self.robot.width, self.robot.height, font_size=self.font_size,
                stroke=self.area_outline, strokewidth=self.outline_size,fill=self.area_fill,outside=True)
        # Drawable Area
        self.add_rect(self.doc,self.robot.x_min, self.robot.y_min, self.robot.img_width, self.robot.img_height, font_size=self.font_size,
                stroke =self.drawable_outline, strokewidth=self.outline_size, fill=self.drawable_fill)

    def draw_codes(self,infile) :
        doc = self.doc
        gcode = open(infile)
        gcodes = gcode.readlines()
        gcode.close()
        x = 0
        y = 0
        pen = 0

        minx = 20000
        miny = 20000
        maxx = -20000
        maxy = -20000
        for line in gcodes:
            move = self.moveCode.match(line)
            dwell = self.dwellCode.match(line)
            pen_cmd = self.penCode.match(line)
            if move:
                xnew = float(move.group(1))
                ynew = float(move.group(2))
                if xnew > maxx:
                        maxx = xnew
                if xnew < minx:
                        minx = xnew
                if ynew > maxy:
                        maxy = ynew
                if ynew < miny:
                        miny = ynew
                if pen:
                        doc.addElement(self.build.createLine(x,y,xnew,ynew,strokewidth=self.pen_size,stroke=self.pen_color))
                x = xnew
                y = ynew
            elif pen_cmd:
                pen_height = int(pen_cmd.group(1))
                pen = pen_height
            elif dwell and pen:
                dwell_time = float(dwell.group(1))
                print "Dwell: ", dwell_time
                drill_amt = drill_size * dwell_prop(dwell_time)
                print "Amt: ", drill_amt
                print "Adding circle of size ",drill_amt," at ", x, ", ",y
                doc.addElement(self.build.createCircle(x, y, r=drill_amt, fill = self.dwell_fill,stroke="none"))
            else:
                pass
        self.add_rect(self.doc,minx, miny, width=maxx-minx, height=maxy-miny, font_size=self.font_size,
                stroke=self.drawing_outline, strokewidth=self.outline_size,inside=False,outside=True)

    def dwell_prop(d) :
        if d > max_dwell:
            return 1
        if d < min_dwell:
            return 0
        return (d - min_dwell) / (max_dwell - min_dwell)

    def add_rect(self,doc,x,y,width,height,stroke,strokewidth,font_size,fill="none",inside=True,outside=False) :
        tlx = x;
        tly = y;
        brx = x+width;
        bry = y+height;
        mrg = font_size/4
        tls = str(tlx)+", "+str(tly)
        brs = str(brx)+", "+str(bry)
        bo = font_size * float(len(brs)) / 2
        doc.addElement(self.build.createRect(x, y, width=width, height=height, stroke=stroke, strokewidth=strokewidth,fill=fill))
        if inside:
            doc.addElement(txt.text(content=tls,x=tlx+mrg,y=tly+5*mrg,	fill=stroke,font_size=font_size))
            doc.addElement(txt.text(content=brs,x=brx+mrg-bo,y=bry-mrg,	fill=stroke,font_size=font_size))
        if outside:
            doc.addElement(txt.text(content=tls,x=tlx+mrg,y=tly-mrg,	fill=stroke,font_size=font_size))
            doc.addElement(txt.text(content=brs,x=brx+mrg-bo,y=bry+5*mrg,	fill=stroke,font_size=font_size))




