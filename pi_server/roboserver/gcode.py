from django import forms

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from threading import Thread
from cursivelib.robocontrol import RobotController
from django.conf import settings

class UploadFileForm(forms.Form):
    file = forms.FileField()

# Quick and dirty multithreading
def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target = function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator

# Handles a gcode file which has been uploaded
@postpone
def handle_gcode(f):
    control = RobotController( port=settings.SERIAL_PORT)
    control.setup_serial()
    d_in = f.read()
    print(d_in)
    data = str(d_in).split('\n')
    print "Got ",len(data)," GCodes to send"
    control.send_robot_commands(data)
    control.finish_serial()

# Ugly, but can't figure out the documentation
@csrf_exempt
def upload_gcode(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_gcode(request.FILES['file'])
            return HttpResponseRedirect('/upload_gcode')
    else:
        form = UploadFileForm()
    return render_to_response('upload_gcode.html', {'form': form})


