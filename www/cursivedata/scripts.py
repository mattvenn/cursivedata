'''
Created on 12 Jan 2013

@author: dmrust
'''
from cursivedata.models import *
from django.utils import timezone
from django.contrib.auth.models import User

def reset_superuser_pw() :
    su = User.objects.all()[0]
    pw = 'admin'
    su.set_password(pw)
    print "Setting password on user ", su, " to ", pw
    su.save()
    
def test_creating_pipeline():
    reset_superuser_pw()
    num = Pipeline.objects.all().count() + 1
    gsq = Generator(name="Squares generator", description="Squares generator", image="No Image", module_name="squares")
    gsq.save()
    gex = Generator(name="Example generator", description="Example generator", image="No Image", module_name="example")
    gex.save()
    gts = Generator(name="graph", description="graph", image="No Image", module_name="graph")
    gts.save()
    gts = Generator(name="test shape", description="test shape", image="No Image", module_name="test_shape")
    gts.save()
    g1 = gts
    g1s = g1.get_state()
    g1s.name = "Generator State for Pipeline " + str(num)
    g1s.save()
    e1 = Endpoint(name="My Robot",device="Polargraph",location="Under the stairs" , width=500, height=400, top_margin=100, side_margin=100)
    e1.save()
    #d1 = DataStore()
    #print d1.id
    #d1.save()
    print("Making pipeline object")
    p1 = Pipeline(name="Test Pipeline " + str(num), generator=g1, endpoint=e1,state=g1s, last_updated=timezone.now() )
    p1.description = "Example pipeline created by test script. Number "+str(num)
    print("Saving pipeline object")
    p1.save()
    print "P1:",str(p1)
    #p1.update(d1)
    ce = COSMSource()
    ce.save()
    ce.pipelines.add(p1)
    ce.save()
    print "COSM:",ce.id
    return {"pipeline":p1, "cosm_source":ce }
