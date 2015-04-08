"""
bugs:
  with squareIncMM an odd number, the squares don't join up properly...
"""
from django.utils.datetime_safe import datetime
import logging
log = logging.getLogger('generator')

def get_minute(date):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    mins =  (minute + hour * 60)/10 # 0 - 143
    return mins

def process(drawing,data,params,internal_state) :

    aggregate = internal_state.get("aggregate",0)
    square_num = int(internal_state.get("square_num",0))
    grid = drawing.get_grid(nx=params.get("Xdiv"),ny=params.get("Ydiv"))
    circle = int(params.get("Circle",0))

    for point in data.get_current():
        cell_index = get_minute(point.date)

        #if we move to a new cell, start small again
        if cell_index != internal_state.get("last_cell",0):
            internal_state["last_cell"] = cell_index
            log.debug("cell index changed")
            aggregate = 0
            square_num = 0

        aggregate += float(point.data['value'])

        #work out where to draw
        cell = grid.cell(cell_index)
        cx, cy = cell.cent()
        
        
        log.debug("number:%d aggregate:%.2f" % (cell_index, aggregate))
        log.debug("x:%d y:%d" % ( cx, cy ))

        #if we have aggregated enough values to draw a square
        while aggregate > params.get("Value"):
            width = params.get("SquareInc") + square_num * params.get("SquareInc")
            log.debug("square #%d width %d" % ( square_num, width ))
            transform = None
            if params.get("Rotate"):
                rotate = int(square_num*params.get("Rotate")) % 360 
                transform = "rotate(%d,%d,%d)" % (rotate,cx,cy)
            hWidth = width/2
            if not circle:
                drawing.rect(cx-hWidth,cy-hWidth,width,width,id=id,transform = transform)
            else:
                drawing.circle(cx,cy,width/2)
                
            aggregate -= params.get("Value")
            #increment squares
            square_num += 1

    internal_state["aggregate"]=aggregate
    internal_state["square_num"]=square_num
    return None

def begin(drawing,params,internal_state) :
    log.info("Starting drawing squares with params: %s" % map(str,params))
    #drawing.tl_text("Started at " + str(datetime.now()),size=15,stroke="blue")
    
def end(drawing,params,internal_state) :
    log.info("Ending drawing")
    content="Ended at " + str(datetime.now()) + " after drawing " + str(internal_state.get("last_cell",0)) + " sets of squares"
    drawing.bl_text(content,stroke="red",size=15)
    
def get_params() :
    return  [ 
        {"name":"Ydiv", "default": 12, "description":"divide paper into y divs" },
        {"name":"Xdiv", "default": 12, "description":"divide paper into x divs" },
        {"name":"SquareInc", "default":2, "description":"amount subsequent squares increase in size" },
        {"name":"Rotate", "default":0, "description":"rotate degrees" },
        {"name":"Value", "default":3000, "description":"value of each square" },
        {"name":"Circle", "default":0, "description":"set to 1 to make circles instead" },
            ]

def get_name() : return "Squares"
def get_description() : return "every 10 minutes start drawing squares about a common point. Each square is worth a certain value. Subsequent squares are drawn larger, and can be rotated"

def can_run(data,params,internal_state):
    aggregate = internal_state.get("aggregate",0)
    last_cell_index = internal_state.get("last_cell",0)
#    import ipdb; ipdb.set_trace()
    for point in data.get_current():
        #if enough time passes, reset aggregate
        cell_index = get_minute(point.date)
        if cell_index != last_cell_index:
            log.debug("resetting aggregate as cell index has changed to %d" % cell_index)
            last_cell_index = cell_index
            aggregate = 0
        aggregate += float(point.getValue())
        if aggregate > params.get("Value"):
            log.debug("squares can run")
            return True
    log.debug("aggregate %s < value %s so not running" % ( aggregate, params.get("Value") ))
  #  internal_state["aggregate"]=aggregate
  #  internal_state["cell_index"]=last_cell_index
    return False

