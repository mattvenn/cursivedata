import ipdb
import datetime
#from django.test import TestCase
import nose.tools as nt
from native_gcode import NativeGCodeConversion, Transform
from svg_to_gcode import SVGPreparation
from svg import create_svg_doc
from pysvg.parser import parse
import pysvg

class Test_native_gcode():

    def setUp(self):
        self.conv = NativeGCodeConversion()
        pass

    #defaults are 0 offset and unit scale
    def test_transform_trans(self):
        t = Transform()
        assert t.transform(10,10) == (10,10)
        assert t.transform(20,20) == (20,20)

    #simple shift
    def test_transform_trans_shift(self):
        t = Transform(xoffset=10,yoffset=-10)
        assert t.transform(10,10) == (20,0)

    #simple scale
    def test_transform_scale(self):
        t = Transform(xscale=2,yscale=-2)
        assert t.transform(100,100) == (200,-200)

    #scale and shift
    def test_transform_scale_and_shift(self):
        t = Transform(xscale=2,yscale=-2,xoffset=100,yoffset=100)
        assert t.transform(100,100) == (300,-100)

    #nested shifts
    def test_transform_shift_nest(self):
        t = Transform(xoffset=10,yoffset=10)
        assert t.transform(0,0) == (10,10)
        u = Transform(xoffset=10,yoffset=10,parent=t)
        assert u.transform(0,0) == (20,20)
        v = Transform(xoffset=10,yoffset=10,parent=u)
        assert v.transform(0,0) == (30,30)
    
    #check nested scales work
    def test_transform_scale_nest(self):
        t = Transform(xscale=2,yscale=2)
        assert t.transform(10,20) == (20,40)
        u = Transform(xscale=2,yscale=2,parent=t)
        assert u.transform(10,20) == (40,80)
        v = Transform(xscale=2,yscale=2,parent=u)
        assert v.transform(10,20) == (80,160)

    #check that own transform is done first before parent's
    #can only test by mixing shift and scale
    def test_transform_scale_and_shift_nest(self):
        t = Transform(xoffset=10,yoffset=10,xscale=2,yscale=2)
        assert t.transform(10,20) == (30,50)
        u = Transform(xoffset=10,yoffset=10,xscale=-1,yscale=-1,parent=t)
        assert u.transform(10,10) == (10,10)
        v = Transform(xoffset=10,yoffset=-10,xscale=-1,yscale=-1,parent=u)
        assert v.transform(10,20) == (30,90)


    def test_convert_svg(self):
        svg_data = parse("square.svg")
        gcode_filename = "gcode.tmp"
        robot_spec = None
        self.conv.convert_svg(svg_data,gcode_filename,robot_spec)
        
        with open(gcode_filename) as fh:
            gcodes = fh.readlines()

        gcodes = [g.strip() for g in gcodes]
        assert gcodes[0] == 'd0'
        assert gcodes[1] == 'g0.0,0.0'
        assert gcodes[2] == 'd1'
        assert gcodes[3] == 'g0.0,200.0'
        assert gcodes[4] == 'g200.0,200.0'

    #good to make this do a multi transform
    def test_convert_transformed_svg(self):
        svg_data = parse("square.svg")
        trans_svg = create_svg_doc(500,500)
        prep = SVGPreparation()
        #make one transform
        tr = pysvg.builders.TransformBuilder()
        tr.setTranslation("10 10")
        trans_svg = prep.apply_into_data(svg_data,trans_svg,tr)

        print trans_svg.getXML()
        gcode_filename = "gcode.tmp"
        robot_spec = None
        self.conv.convert_svg(trans_svg,gcode_filename,robot_spec)

        with open(gcode_filename) as fh:
            gcodes = fh.readlines()

        gcodes = [g.strip() for g in gcodes]
        assert gcodes[0] == 'd0'
        assert gcodes[1] == 'g10.0,10.0'
        assert gcodes[2] == 'd1'
        assert gcodes[4] == 'g210.0,210.0'

    """
    def test_pipeline(self):
        self.conv.convert_svg(robot_svg,output_filename,self.robot_spec)
        nt.assert_equal(self.pipeline.get_output_name(), "pipeline" )
    """
