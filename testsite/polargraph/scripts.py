'''
Created on 12 Jan 2013

@author: dmrust
'''
from polargraph.models import *
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
    g1 = Generator(name="Square Generator", description="This is a generator to test stuff with", image="No Image", module_name="squares")
    g1.save()
    g1.init()
    g1s = g1.get_state()
    g1s.name = "Generator State for Pipeline " + str(num)
    g1s.save()
    e1 = Endpoint(name="My Robot",device="Polargraph",location="Under the stairs" , width=500, height=500, top_margin=100, side_margin=100)
    e1.save()
    d1 = DataStore()
    print d1.id
    d1.save()
    p1 = Pipeline(name="Test Pipeline " + str(num),data_store=d1, generator=g1, endpoint=e1,state=g1s, last_updated=timezone.now() )
    p1.description = "Example pipeline created by test script. Number "+str(num)
    p1.save()
    print "P1:",str(p1)
    g1.init()
    p1.update(d1)
    ce = COSMSource(data_store=d1)
    ce.save()
    print "COSM:",ce.id
    return {"pipeline":p1, "data_store":d1, "cosm_source":ce }
