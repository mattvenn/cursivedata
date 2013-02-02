from django.utils.datetime_safe import datetime


def process(drawing,data,params,internal_state) :
    print "Example Processing data with parameters",map(str,params)
    
    #Read in parameters
    it = internal_state.get("i",0) 
    sat = params.get("Saturation",1.0)
    lev = params.get("Level",0.5)
    
    #Set up variables which stay constant for each point
    grid = drawing.get_grid(nx=int(params.get("Number",6)))
    w = grid.size_x
    
    #Run through all the data points
    for point in data.get_current():
        val = ((float(point['value'])/34000.0))
        cell = grid.cell(it)
        tlx, tly = cell.tl()
        cx, cy = cell.cent()
        radius = val*w/2
        drawing.rect(tlx,tly,w, w)
        drawing.circle(cx, cy, radius, fill=drawing.hsv_to_color(val,sat,lev) )
        it = it+1
        
    #Write back any state we want to keep track of
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