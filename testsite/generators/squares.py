"""
bugs:
  with squareIncMM an odd number, the squares don't join up properly...
"""
from django.utils.datetime_safe import datetime

def get_minute(date):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    mins =  (minute + hour * 60)/10 # 0 - 143
    return mins

def process(drawing,data,params,internal_state) :

    aggregate = internal_state.get("aggregate",0)
    square_num = int(internal_state.get("square_num",0))
    grid = drawing.get_grid(nx=params.get("Xdiv"),ny=params.get("Ydiv"))
    key = 'light'

    for point in data.get_current():
        aggregate += float(point[key])
        #allow user to determine how fast the graph is drawn again
        cell_index = get_minute(point['time'])
        #work out where to draw
        cell = grid.cell(cell_index)
        cx, cy = cell.cent()
        
        #if we move to a new cell, start small again
        if cell_index != internal_state.get("last_cell",0):
            internal_state["last_cell"] = cell_index
            print "reset square num"
            square_num = 0
        
        print "number:%d\naggregate:%.2f" % (cell_index, aggregate)
        print "x:%d y:%d" % ( cx, cy )

        #if we have aggregated enough values to draw a square
        while aggregate > params.get("Value"):
            width = params.get("SquareInc") + square_num * params.get("SquareInc")
            print "square #%d width %d" % ( square_num, width )
            transform = None
            if params.get("Rotate"):
                rotate = int(square_num*params.get("Rotate")) % 360 
                transform = "rotate(%d,%d,%d)" % (rotate,cx,cy)
            hWidth = width/2
            drawing.rect(cx-hWidth,cy-hWidth,width,width,id=id,transform = transform)
            aggregate -= params.get("Value")
            #increment squares
            square_num += 1

    internal_state["aggregate"]=aggregate
    internal_state["square_num"]=square_num
    return None

def begin(drawing,params,internal_state) :
    print "Starting drawing squares: ",map(str,params)
    drawing.tl_text("Started at " + str(datetime.now()),size=15,stroke="blue")
    
def end(drawing,params,internal_state) :
    print "Ending exmaple drawing with params:",map(str,params)
    content="Ended at " + str(datetime.now()) + " after drawing " + str(internal_state.get("last_cell",0)) + " sets of squares"
    drawing.bl_text(content,stroke="red",size=15)
    
def get_params() :
    return  [ 
        {"name":"Ydiv", "default": 12, "description":"divide paper into y divs" },
        {"name":"Xdiv", "default": 12, "description":"divide paper into x divs" },
        {"name":"SquareInc", "default":2, "description":"amount subsequent squares increase in size" },
        {"name":"Rotate", "default":0, "description":"rotate degrees" },
        {"name":"Value", "default":3000, "description":"value of each square" },
            ]

def get_name() : return "Squares"
def get_description() : return "every 10 minutes start drawing squares about a common point. Each square is worth a certain value. Subsequent squares are drawn larger, and can be rotated"

def can_run(data,params,internal_state):
    #run every time
    key = 'light'
    aggregate = internal_state.get("aggregate",0)
    for point in data.get_current():
        aggregate += float(point[key])
        if aggregate > params.get("Value"):
            return True
    print "aggregate %f < value %f so not running" % ( aggregate, params.get("Value") )
    return False

