"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import pdb
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from polargraph.models import *
from django.utils import timezone
from polargraph.drawing import Drawing

from pysvg.structure import svg
from pysvg.builders import ShapeBuilder
from pysvg.text import text

from polargraph.svg import append_svg_to_file
from pysvg.parser import parse

from django.utils import timezone
import nose.tools as nt

"""
#class SimpleTest(TestCase):
class SimpleTest():
    def test_basic_addition(self):
        self.assertEqual(1 + 1, 2)

"""
class TestPipeline():

    def setup(self):
        self.generator = Generator(name="Squares generator", description="Squares generator", image="No Image", module_name="squares")
        self.generator.save()
    
        self.gen_state = self.generator.get_state()
        self.gen_state.name = "Generator State for Pipeline"
        self.gen_state.save()

        self.data_store = DataStore()
        self.data_store.save()

        self.end_point = Endpoint(name="My Robot",device="Polargraph",location="Under the stairs" , width=500, height=400, top_margin=100, side_margin=100)
        self.end_point.save()

        self.pipeline = Pipeline(name="Test Pipeline" ,data_store=self.data_store, generator=self.generator, endpoint=self.end_point,state=self.gen_state, last_updated=timezone.now() )

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

    def test_update_data(self):
        #data is less than needed to run pipeline
        data = [{ 'value' : 1000 }]
        self.data_store.add_data(data)
        nt.assert_equal(self.data_store.load_current()[0]['value'],data[0]['value'] )
        #would be good to check time deserialization

    def test_run_pipeline(self):
        #data is what is needed to run pipeline
        data = [{ 'value' : 4000 }]
        self.data_store.add_data(data)
        gcode = open(self.end_point.get_next_filename()).readlines()
        gcode = [ s.strip() for s in gcode ]
        #use a shape generator and actually check real gcodes
        nt.assert_equal(gcode[0],'d0')



        

"""

class SVGTest():
    def test_appending(self):
        frag_file="tmp/b.svg"
        main_file="tmp/a.svg"
        main = svg()
        frag = svg()
        exp = svg()
        sb = ShapeBuilder()
        
        main.addElement(sb.createRect(0, 0, "200px", "100px"))
        exp.addElement(sb.createRect(0, 0, "200px", "100px"))
        
        frag.addElement(text("Hello World", x = 210, y = 110))
        exp.addElement(text("Hello World", x = 210, y = 110))
        main.save(main_file)
        frag.save(frag_file)
        append_svg_to_file(frag_file,main_file)
        
        svg_main = parse(main_file)
        gotS =str(svg_main.getXML())
        expS = str(exp.getXML())
        print"Got:",gotS
        print"Exp:",expS
        #self.assertEqual(exp.getXML(), svg_main.getXML(), "Appended files are equal" )
        if gotS != expS :
            print "Different\nGot:\n",gotS,"\nExp:\n",expS
        #self.assertEqual(exp.getXML(), svg_main.getXML(), "Appended files are equal" )
        
        
        
"""
