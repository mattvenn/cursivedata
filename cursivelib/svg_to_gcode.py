import pysvg.structure
import pysvg.builders
from pysvg.parser import parse

import cursivelib.svg as svg


class SVGPreparation() :


    # Returns an SVG transform which puts the SVG at the given 
    # place on the page
    def get_drawing_transform(self, drawing_position) :
        tr = pysvg.builders.TransformBuilder()
        tr.setScaling(drawing_position.scale)
        trans = str(drawing_position.xoffset) + " " + str(drawing_position.yoffset) 
        tr.setTranslation( trans )
        return tr


    # Returns an SVG transform which will convert screen SVG to
    # robot coordinate SVG
    # SVG coords are 0,0 in bottom left, while robot it is
    # 0,0 in top left. So we flip the y axis and offset by
    # drawing height
    def get_robot_transform(self,robot_spec) :
        #setup our transform
        tr = pysvg.builders.TransformBuilder()
        tr.setScaling(x=1,y=-1)
        trans = str(robot_spec.side_margin) + " " + str(robot_spec.img_height) 
        tr.setTranslation( trans )
        return tr



    # Takes SVG data, applies a transform to it, and returns
    # the group element with the transformed data
    def apply_transform(self,svg_data,transform) :
        group = pysvg.structure.g()
        group.set_transform(transform.getTransform())

        for element in svg_data.getAllElements():
            group.addElement(element)
        return group

    # Transforms the source data and adds it into the target data
    def apply_into_data(self,source_data,target_data,transform) :
        transformed = self.apply_transform(source_data,transform)
        target_data.addElement(transformed)
        return target_data

    #could do clipping? http://code.google.com/p/pysvg/source/browse/trunk/pySVG/src/tests/testClipPath.py?r=23
    #def do_clipping(self,svg_data,robot_spec)

    # Goes from an SVG file, a DrawingSpec and a RobotSpec to a
    # DrawingPosition which can be used to locate the drawing on
    # the page. RobotSpec is just used for checking dimensions
    # Currently, just puts the drawing top center; DrawingSpec
    # could be expanded to do something more clever
    def drawing_position_from_file(self, svg_filename, drawing_spec, robot_spec=None ) :
        (svgwidth,svgheight) = svg.get_dimensions(file(svg_filename))
        width = drawing_spec.width
        if robot_spec is not None :
            if width > robot_spec.img_width:
                print "not scaling larger than endpoint"
                err = "width %d is too large for endpoint, max width is %d" % (width, robot_spec.img_width)
                raise Exception(err )
            if width == 0:
                print "not using a 0 width"
                width = robot_spec.img_width

        #put it in the middle of the page
        return DrawingPosition(
            xoffset = (robot_spec.img_width - width ) / 2,
            yoffset = 0,
            scale = width / svgwidth
            )




class DrawingSpec() :
    def __init__(self,width,location="top_center") :
        self.width = width


class DrawingPosition() :
    def __init__(self,xoffset=0,yoffset=0,scale=1) :
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.scale = scale

    def show(self):
        print "Scale: " , self.scale
        print "X Offset: " , self.xoffset
        print "Y Offset: " , self.yoffset

