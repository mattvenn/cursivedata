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

def doc_width(svg_document):
        return float(str(svg_document.get_width()).replace("mm",""))
def doc_height(svg_document):
        return float(str(svg_document.get_height()).replace("mm",""))

def begin(svg_document,params,internal_state) :
    print "Starting example drawing with params: ",map(str,params)
    text = txt.text(content="Started at " + str(datetime.now()),x=10,y=10,fill="blue")
    text.set_font_size(10);
    text.set_font_family("Verdana")
    svg_document.addElement( text )
    
def end(svg_document,params,internal_state) :
    print "Ending exmaple drawing with params:",map(str,params)
    content="Ended at " + str(datetime.now()) + " after drawing " + str(internal_state.get("i",0)) + " updates"
    text = txt.text(content=content,x=10,y=doc_height(svg_document)-10,fill="red")
    text.set_font_size(10);
    text.set_font_family("Verdana")
    svg_document.addElement( text )
    
def get_params() :
    return  [ 
             { "name":"Number", "default": 10, "description":"The number of outputs to have horizontally and vertically" }, 
             { "name":"Saturation", "default":0.6, "description":"Saturation of the colour (0-1)" },
             {"name":"Level", "default": 0.9, "description":"Brightness of the colour (0-1)" }] 

def get_name() : return "Example Generator"
def get_description() : return "Description of Example Generator"

def can_run(data,params,internal_state):
    return True;