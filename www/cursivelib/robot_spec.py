
import cursivelib.svg as svg
import re

class RobotSpec() :
    def __init__(self,width,height,top_margin,side_margin):
        self.width = width
        self.height = height
        self.top_margin = top_margin
        self.side_margin = side_margin
        self.img_width = self.width - self.side_margin * 2
        self.img_height = self.height - self.top_margin
        self.x_min = self.side_margin
        self.y_min = self.top_margin
        self.x_max = self.side_margin + self.img_width
        self.y_max = self.top_margin + self.img_height

    def write_outline_gcode(self,filename):
        f = open(filename,'w')
        f.write("g%.1f,%.1f\n" % ( self.side_margin, self.top_margin ))
        f.write("g%.1f,%.1f\n" % ( self.width - self.side_margin , self.top_margin ))
        f.write("g%.1f,%.1f\n" % ( self.width - self.side_margin , self.height ))
        f.write("g%.1f,%.1f\n" % ( self.side_margin , self.height ))
        f.write("g%.1f,%.1f\n" % ( self.side_margin, self.top_margin ))
        f.close()

    def write_calibration_gcode(self,filename):
        f = open(filename,'w')
        f.write("c\n")
        f.close()

    

    # Returns an SVG object in drawing coords, sized to the full printing area
    def svg_drawing(self) :
        return svg.create_svg_doc(self.img_width,self.img_height)

    # Returns an SVG object representing the whole area, including margins
    def svg_total(self) :
        return svg.create_svg_doc(self.width,self.height)

# Expects a string with height,width,topmargin, sidemargin
def string_to_spec(details) :
    nums = re.compile( "^(\\d+),(\\d+),(\\d+),(\\d+)$")
    m = nums.match(details)
    if m:
        print "got data: ", m.group(1),", ",m.group(2),", ",m.group(3),", ",m.group(4)
        return RobotSpec(float(m.group(1)),float(m.group(2)),float(m.group(3)),float(m.group(4)))
    else:
        print "Coudln't parse robot spec: ",details
            

