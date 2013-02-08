"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from polargraph.models import *
from django.utils import timezone

from pysvg.structure import svg
from pysvg.builders import ShapeBuilder
from pysvg.text import text

from polargraph.svg import append_svg_to_file
from pysvg.parser import parse

#class SimpleTest(TestCase):
class SimpleTest():
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_creating_pipeline(self):
        g1 = Generator(name="Test Generator", description="This is a fake generator to test stuff with", image="No Image", module_name="example")
        g1.save()
        g1p = Parameter(name="Param 1",generator=g1)
        g1p.save()
        g1s = GeneratorState(name="Current",generator=g1)
        g1s.save()
        e1 = Endpoint(name="My Robot",device="Polargraph",location="Under the stairs" )
        e1.save()
        d1 = DataStore()
        print d1.id
        d1.save()
        p1 = Pipeline(name="Test Pipeline",data_store=d1, generator=g1, endpoint=e1,state=g1s, last_updated=timezone.now() )
        p1.save()
        print "P1:",str(p1)
        p1.update()
        ce = COSMSource(data_store=d1)
        ce.save()
        print "COSM:",ce.id
        return {"pipeline":p1, "data_source":d1, "cosm_source":ce }

    
    
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
        
        
        