"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from polargraph.models import *
from django.utils import timezone


class SimpleTest(TestCase):
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
        g1p1s = GeneratorStateParameter(state=g1s,parameter=g1p,value=7)
        g1p1s.save()
        e1 = Endpoint(name="My Robot",device="Polargraph",location="Under the stairs" )
        e1.save()
        d1 = DataStore()
        print d1.id
        d1.save()
        p1 = Pipeline(name="Test Pipeline",data_store=d1, generator=g1, endpoint=e1,state=g1s, last_updated=timezone.now() )
        p1.save()
        print "P1:",str(p1)
        g1.init()
        p1.update()
        ce = COSMSource(data_store=d1)
        ce.save()
        print "COSM:",ce.id
        return {"pipeline":p1, "data_source":d1, "cosm_source":ce }

    
    
 
