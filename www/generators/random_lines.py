from django.utils.datetime_safe import datetime
import random
import logging
log = logging.getLogger('generator')

def process(drawing,data,params,internal_state) :
    
    #Read in parameters
    stroke_width = params.get("Stroke Width",0.1)
    max = params.get("Data Max",100)
    min = params.get("Data Min",0)
    min_height = params.get("Min Height",0.8)
    max_height = params.get("Max Height",0.8)
    min_density = params.get("Min Density",20)
    max_density = params.get("Max Density",20)
    npoints = int(params.get("Points per strip",20))
    strips = int(params.get("Vertical Strips",30))
    log.debug("Num strips: %s" % strips)

    #Read in state
    current = internal_state.get("current",None) 
    last_row = internal_state.get("row",None) 
    it = internal_state.get("i",0) 
    
    #Set up variables which stay constant for each point
    grid = drawing.get_grid(nx=npoints,ny=strips,force_square=False)
    w = grid.size_x
    h = grid.size_y
    log.debug("Grid : %d x %d" % (w, h))
    
    #Run through all the data points
    for point in data.get_current():
        initial = float(point.getValue())
        val = ( initial-min)  / ( max - min )
        log.debug("Data value %s" % val)
        
        cell = grid.cell(it)
        if( cell.x != last_row ): #When we start a new row, don't draw from the last point
            last_row = cell.x
            current = None
        cx, cy = cell.cent()
        lx, ly = cell.tl()

        avg_height = ( val * (max_height-min_height) + min_height ) * h
        density = ( val * (max_density-min_density) + min_density ) 
        for i in range(0,density):
            current = draw_line(drawing,lx + (w*(i/density)),cy,w,avg_height,stroke_width,current)
        it = it+1
        
    #Write back any state we want to keep track of
    internal_state["i"]=it
    internal_state["current"]=current
    internal_state["row"]=last_row
    return None

def draw_line(drawing,x,y,width,height,stroke_width,current=None):
    if( not current ):
        current = get_point(x,y,width,height)
    next = get_point(x,y,width,height)
    drawing.line(current[0],current[1],next[0],next[1],strokewidth=str(stroke_width))
    return next

def get_point(x,y,width,height):
    return (random.uniform(x-width/2,x+width/2),random.uniform(y-height/2,y+height/2))

def begin(drawing,params,internal_state) :
    log.info("Starting random lines drawing with params: %s" % params)
    #drawing.tl_text("Started at " + str(datetime.now()),fill="blue",size=15)
    
def end(drawing,params,internal_state) :
    log.info("Ending drawing")
    content="Ended at " + str(datetime.now()) + " after drawing " + str(internal_state.get("i",0)) + " updates"
    #drawing.bl_text(content,fill="red",size="30")
    
def get_params() :
    return  [ 
             { "name":"Stroke Width", "default": 0.1, "description":"Width of strokes to use for drawing" }, 
             { "name":"Data Max", "default": 1000, "description":"Maximum expected data value" }, 
             { "name":"Data Min", "default": 0, "description":"Minimum expected data value" }, 
             { "name":"Points per strip", "default": 20, "description":"The number of points per strip" }, 
             { "name":"Vertical Strips", "default": 10, "description":"The number of strips to have vertically" }, 
             { "name":"Min Height", "default": 0.2, "description":"Minimum height of each strip as a proportion of strip height" }, 
             { "name":"Max Height", "default": 1.2, "description":"Maximum height of each strip as a proportion of strip height" }, 
             { "name":"Min Density", "default": 10, "description":"Minimum number of lines to draw per strip" },
             { "name":"Max Density", "default": 40, "description":"Maximum number of lines to draw per strip" } 
             ] 

def get_name() : return "Example Generator"
def get_description() : return "Description of Example Generator"

def can_run(data,params,internal_state):
    return True
