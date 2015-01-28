import ipdb
import datetime
#from django.test import TestCase
import nose.tools as nt
from native_gcode import NativeGCodeConversion, Transform


class Test_native_gcode():

    def setUp(self):
        #self.conv = NativeGCodeConversion()
        pass

    def test_transform_trans(self):
        t = Transform()
        assert t.transform(10,10) == (10,10)
        assert t.transform(20,20) == (20,20)

    def test_transform_trans_shift(self):
        t = Transform(xoffset=10,yoffset=-10)
        assert t.transform(10,10) == (20,0)

    def test_transform_scale(self):
        t = Transform(xscale=2,yscale=-2)
        assert t.transform(100,100) == (200,-200)

    def test_transform_shift_nest(self):
        t = Transform(xoffset=10,yoffset=10)
        assert t.transform(0,0) == (10,10)
        u = Transform(xoffset=10,yoffset=10,parent=t)
        assert u.transform(0,0) == (20,20)
        v = Transform(xoffset=10,yoffset=10,parent=u)
        assert v.transform(0,0) == (30,30)
    
    def test_transform_scale_nest(self):
        t = Transform(xscale=2,yscale=2)
        assert t.transform(10,20) == (20,40)
        u = Transform(xscale=2,yscale=2,parent=t)
        assert u.transform(10,20) == (40,80)
        v = Transform(xscale=2,yscale=2,parent=u)
        assert v.transform(10,20) == (80,160)

    def test_transform_nest(self):
        t = Transform(xoffset=10,yoffset=10,xscale=2,yscale=2)
        assert t.transform(10,20) == (30,50)
        u = Transform(xoffset=10,yoffset=10,xscale=-1,yscale=-1,parent=t)
        assert u.transform(10,20) == (-20,-40)
        v = Transform(xoffset=-10,yoffset=-10,xscale=-1,yscale=-1,parent=u)
        assert v.transform(10,20) == (10,30)


    """
    def test_pipeline(self):
        self.conv.convert_svg(robot_svg,output_filename,self.robot_spec)
        nt.assert_equal(self.pipeline.get_output_name(), "pipeline" )
    """
