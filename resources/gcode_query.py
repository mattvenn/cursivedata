
import sys
import os
import datetime
 
sys.path.insert(0, os.path.expanduser('~/cursivedata/www'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

from cursivedata.models import *
from cursivedata.models.endpoint import GCodeOutput

ep_id = 2
ep = Endpoint.objects.get(id=ep_id)
print ep.name, "id", ep_id


#import ipdb; ipdb.set_trace()

total_gcodes = GCodeOutput.objects.filter(endpoint=ep).count()
fresh_gcodes = GCodeOutput.objects.filter(endpoint=ep,served=False)
print "%d total_gcodes of which %d left to be served" % ( total_gcodes, len(fresh_gcodes))

no_data = 0
no_file = 0
for gcode in fresh_gcodes:
    gcode_path = gcode.get_filename()
    try:
        if os.path.getsize(gcode_path) == 0:
            #print "gcode file for %d doesn't have data" % gcode.id
            no_data += 1
    except OSError:
        #print "gcode file for %d doesn't exist" % gcode.id
        no_file += 1
   
print "of %d unserved files, %d don't have data and %d don't have files" % (len(fresh_gcodes),no_data,no_file)


fixed = 0
for gcode in fresh_gcodes:
    gcode_path = gcode.get_filename()
    try:
        if os.path.getsize(gcode_path) == 0:
            pass
    except OSError:
        print "fixing gcode for %d" % gcode.id
        #import pdb; pdb.set_trace()
        #pretend we've served it
        gcode.served = True
        gcode.save()
        fixed +=1
   
print "fixed %d bad files" % (fixed)


