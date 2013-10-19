
import argparse
import sys
import os
import datetime
path = '/home/polarsite/cursivedata/www/'
sys.path.insert(0, os.path.expanduser(path))
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

from cursivedata.models import *
from cursivedata.models.endpoint import GCodeOutput

parser = argparse.ArgumentParser(description="manage gcode files")
parser.add_argument('--id', action='store', type=int, dest='ep_id', help="endpoint id", required=True)
parser.add_argument('--fix-all', action='store_const', const=True, default=False, dest='fix_all', help="mark all the broken gcode files as served")

args = parser.parse_args()

ep = Endpoint.objects.get(id=args.ep_id)
print ep.name, "id", args.ep_id

#print a summary
total_gcodes = GCodeOutput.objects.filter(endpoint=ep).count()
fresh_gcodes = GCodeOutput.objects.filter(endpoint=ep,served=False)
print "%d total_gcodes of which %d left to be served" % ( total_gcodes, len(fresh_gcodes))

#for all the gcode files, find which ones have problems
no_data = 0
no_file = 0
for gcode in fresh_gcodes:
    gcode_path = path + gcode.get_filename()
    try:
        if os.path.getsize(gcode_path) == 0:
            #print "gcode file for %d doesn't have data" % gcode.id
            no_data += 1
    except OSError:
        #print "gcode file for %d doesn't exist: %s" % ( gcode.id, gcode_path )
        no_file += 1
   
print "of %d unserved files, %d don't have data and %d don't have files" % (len(fresh_gcodes),no_data,no_file)
if no_file:
    print "use --fix-all to fix missing files"

#to fix the, we just mark them served
if args.fix_all:
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
