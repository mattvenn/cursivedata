"""
run "manage.py test".
"""

import ipdb
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from cursivedata.models import *
from django.utils import timezone
from cursivedata.drawing import Drawing

from pysvg.structure import svg
from pysvg.builders import ShapeBuilder
from pysvg.text import text

from cursivedata.svg import append_svg_to_file
from pysvg.parser import parse

from django.utils import timezone
import nose.tools as nt

class TestPipeline(TestCase):

    def setUp(self):
        self.generator = Generator(name="shapes", description="shapes", image="No Image", module_name="test_shape")
        self.generator.save()
    
        self.gen_state = self.generator.get_state()
        self.gen_state.name = "Generator State for Pipeline"
        self.gen_state.save()

        self.data_store = DataStore()
        self.data_store.save()

        self.end_point = Endpoint(name="My Robot",device="Polargraph",location="Under the stairs" , width=1000, height=1000, top_margin=100, side_margin=100,generate_gcode=True)
        self.end_point.save()

        self.pipeline = Pipeline(name="Test Pipeline" ,data_store=self.data_store, generator=self.generator, endpoint=self.end_point,state=self.gen_state, last_updated=timezone.now() )
        self.pipeline.save()

        #set to same size as robot
        self.svg_doc =self.pipeline.create_svg_doc()
        self.drawing = Drawing(self.svg_doc)

    def test_pipeline(self):
        nt.assert_equal(self.pipeline.get_output_name(), "pipeline" )

    def test_drawing(self):
        nt.assert_equal(self.drawing.width, 500 )
        nt.assert_equal(self.drawing.height, 500 )

    def test_grid(self):
        xdiv =12 
        ydiv = 12
        dwg_x = 400
        dwg_y = 400

        grid = self.drawing.get_grid(xdiv,ydiv)    
        offsetx = grid.offset_x
        offsety = grid.offset_y
        cell_w = grid.size_x
        cell_h = grid.size_y

        nt.assert_equal( grid.nx, xdiv)
        nt.assert_equal( grid.ny, ydiv)

        #index
        for row in range(xdiv):
            for col in range(ydiv):
                nt.assert_equal( grid.index_to_xy(row+col*xdiv), (row,col))

        #pdb.set_trace()
        #top left dimensions
        for row in range(xdiv):
            for col in range(ydiv):
                nt.assert_equal( grid.cell(row+col*xdiv).tl(), (row*cell_w,col*cell_h))

        #centre dimensions
        for row in range(xdiv):
            for col in range(ydiv):
                nt.assert_equal( grid.cell(row+col*xdiv).cent(), (row*cell_w+cell_w/2,col*cell_h+cell_h/2))

    """ this won't work for the test_shape generator
    def test_update_data(self):
        #data is less than needed to run pipeline
        data = [{ 'value' : 1000 }]
        self.data_store.add_data(data)
        nt.assert_equal(self.data_store.load_current()[0]['value'],data[0]['value'] )
        #would be good to check time deserialization
    """
   
    def test_100mm_square(self):
        sq_height = 100
        sq_width  = 100

        self.gen_state.params['x']=0
        self.gen_state.params['y']=0
        self.gen_state.params['Width']=sq_width
        self.gen_state.params['Height']=sq_height
        self.gen_state.save()

        self.run_and_check_size(sq_height,sq_width)

    def test_200mm_square(self):
        sq_height = 200
        sq_width  = 200

        self.gen_state.params['x']=0
        self.gen_state.params['y']=0
        self.gen_state.params['Width']=sq_width
        self.gen_state.params['Height']=sq_height
        self.gen_state.save()

        self.run_and_check_size(sq_height,sq_width)

    def run_and_check_size(self,sq_height,sq_width):
        #this runs the pipeline
        timestamp = str(timezone.now())
        data = [{ 'data' : '{"value":4000}', "date" : timestamp }]
        import pdb; pdb.set_trace()
        self.data_store.add_data(data)

        #robot margins
        side_m = self.end_point.side_margin
        top_m = self.end_point.top_margin
        
        gcode = open(self.end_point.get_next_filename()).readlines()
        gcode = [ s.strip() for s in gcode ]

        #better way to do this?
        nt.assert_equal(gcode[0],'d0')
        nt.assert_equal(gcode[1],'g%d.0,%d.0' % (side_m,top_m+sq_height))
        nt.assert_equal(gcode[2],'d1')
        nt.assert_equal(gcode[3],'g%d.0,%d.0' % (side_m+sq_width,top_m+sq_height))
        nt.assert_equal(gcode[4],'g%d.0,%d.0' % (side_m+sq_width,top_m))
        nt.assert_equal(gcode[5],'g%d.0,%d.0' % (side_m,top_m))
        nt.assert_equal(gcode[6],'g%d.0,%d.0' % (side_m,top_m+sq_height))
        nt.assert_equal(gcode[7],'d0')

    """
    self.pipeline.update_size(300,300)
    self.pipeline.print_width = 300
    self.pipeline.print_top_left_x = 0
    self.pipeline.print_top_left_y = 0
    self.pipeline.save()
    """
    """
    def test_run_pipeline(self):
        #data is what is needed to run pipeline
        data = [{ 'value' : 4000 }]

        #set robot margins
        end_point = Endpoint(name="My Robot",device="Polargraph",location="Under the stairs" , width=500, height=400, top_margin=100, side_margin=100)
        #set pipeline so there is no scaling
        self.pipeline.update_size(300,300)
        self.pipeline.print_width = 300
        self.pipeline.print_top_left_x = 0
        self.pipeline.print_top_left_y = 0
        self.pipeline.save()
        self.gen_state.params['x']=0
        self.gen_state.params['y']=0
        self.gen_state.params['Width']=100
        self.gen_state.params['Height']=100
        self.gen_state.save()

        #this runs the pipeline
        self.data_store.add_data(data)
        gcode = open(self.end_point.get_next_filename()).readlines()
        gcode = [ s.strip() for s in gcode ]
        #use a shape generator and actually check real gcodes
        #better way to do this?
        nt.assert_equal(gcode[0],'d0')
        nt.assert_equal(gcode[1],'g100.0,200.0')
        nt.assert_equal(gcode[2],'d1')
        nt.assert_equal(gcode[3],'g200.0,200.0')
        nt.assert_equal(gcode[4],'g200.0,100.0')
        nt.assert_equal(gcode[5],'g100.0,100.0')
        nt.assert_equal(gcode[6],'g100.0,200.0')
        nt.assert_equal(gcode[7],'d0')
        
    """



        
