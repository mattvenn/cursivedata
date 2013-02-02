import pysvg.text as txt
import pysvg
import colorsys
from django.utils.datetime_safe import datetime


def process(drawing,data,params,internal_state) :
    print "Example Processing data with parameters",map(str,params)
    #print "Example internal state: ",internal_state
    #print "Internal State: ",internal_state.get("i","None")
    it = internal_state.get("i",0) 
    
    for point in data.get_current():
        num = int(params.get("Number",6))
        cell_width = drawing.width/num
        cws = str(cell_width)
        xp = ((it)%num)*cell_width
        yp = (((it)/num)%num)*cell_width
        w = ((float(point['value'])/34000.0))*cell_width/2
        wp = str(w)
        hue = float(point['value'])/34000.0
        sat = params.get("Saturation",1.0)
        lev = params.get("Level",0.5)
        rgbs = drawing.hsv_to_color(hue,sat,lev)
        drawing.rect(xp,yp,cws, cws)
        drawing.circle(xp+cell_width/2, yp+cell_width/2, wp, fill=rgbs )
        it = it+1
    internal_state["i"]=it
    return None

def begin(drawing,params,internal_state) :
    print "Starting example drawing with params: ",map(str,params)
    drawing.tl_text("Started at " + str(datetime.now()),fill="blue",size=15)
    
def end(drawing,params,internal_state) :
    print "Ending exmaple drawing with params:",map(str,params)
    content="Ended at " + str(datetime.now()) + " after drawing " + str(internal_state.get("i",0)) + " updates"
    drawing.bl_text(content,fill="red",size="30")
    
def get_params() :
    return  [ 
             { "name":"Number", "default": 10, "description":"The number of outputs to have horizontally and vertically" }, 
             { "name":"Saturation", "default":0.6, "description":"Saturation of the colour (0-1)" },
             {"name":"Level", "default": 0.9, "description":"Brightness of the colour (0-1)" }] 

def get_name() : return "Example Generator"
def get_description() : return "Description of Example Generator"

def can_run(data,params,internal_state):
    return True;