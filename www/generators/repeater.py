from django.utils.datetime_safe import datetime
from pysvg.builders import *
import pysvg.structure
import logging
from cursivedata.mapping import mapping
log = logging.getLogger('generator')


def get_division(date,params):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int( date.strftime("%H") ) # hours 0 - 23
    dom = int( date.strftime("%d") ) #day of month 0 - 31
    #mins in a month
    mins =  minute + hour * 60 + dom * 24 * 60

    total_cells = params.get('Xdiv') * params.get('Ydiv')
    division = mins / int(params.get('Total_time') / total_cells)
    division = division % total_cells
    return int(division)

def get_group_with_xform(shape, transform):
    group = pysvg.structure.g()
    group.set_transform(transform.getTransform())
    group.addElement(shape)
    return group

def draw_shape(drawing, filename, x, y, size, flip, shape_size):
    shape = drawing.get_first_group_from_file("media/repeater/" + filename)

    #how to get this?
    x -= size * shape_size/2
    y -= size * shape_size/2


    # scale
    tr = TransformBuilder()
    if flip:
        tr.setScaling(-size,size) 
        # it will be flipped so have to add its width to x
        x += size * shape_size
        x += shape_size / 2
    else:
        tr.setScaling(size,size) 
    shape = get_group_with_xform(shape, tr)

    # translate
    tr = TransformBuilder()
    tr.setTranslation("%d,%d" % (x,y))
    shape = get_group_with_xform(shape, tr)

    drawing.doc.addElement(shape)

def draw_shape_on_grid(drawing, cell_index, aggregate, params):
    #work out where to draw
    grid = drawing.get_grid(nx=params.get("Xdiv"), ny=params.get("Ydiv"))
    grid_col, grid_row = grid.index_to_xy(cell_index)
    cell = grid.cell(cell_index)
    cx, cy = cell.cent()
    shape_size = float(params.get("Shape Size", 1))
    unit_size = drawing.width / (shape_size * float(params.get("Xdiv")))
    #map the aggregate to the scale
    m = mapping(params.get("In Min"), params.get("In Max"), params.get("Out Min"), params.get("Out Max"))
    size = unit_size * m.map(aggregate)
    svg_file = params.get("Shape")
    flip = params.get("Flip", False)
    log.debug("drawing shape %s at x:%d y:%d scale %f flipped %s" % (svg_file, cx, cy, size, flip))

    if flip and grid_row % 2 == 0:
        draw_shape(drawing, svg_file, cx, cy, size, True, shape_size)
    else:
        draw_shape(drawing, svg_file, cx, cy, size, False, shape_size)

def process(drawing,data,params,internal_state) :
    aggregate = internal_state.get("aggregate",0)

    # process all current data
    for point in data.get_current():
        # find out which cell we're on
        cell_index = get_division(point.date, params)
        log.debug("date %s = %d" % (point.date, cell_index))

        #if we move to a new cell, draw the shape
        if cell_index != internal_state.get("cell_index", 0):
            log.debug("cell index changed")
            draw_shape_on_grid(drawing, internal_state.get("cell_index", 0), aggregate, params) 
            # update cell index
            internal_state["cell_index"] = cell_index
            # reset aggregate
            aggregate = 0

        aggregate += float(point.getValue())

        log.debug("number:%d aggregate:%.2f" % (cell_index, aggregate))

    internal_state["aggregate"]=aggregate
    return None

def begin(drawing,params,internal_state) :
    log.info("Starting drawing repeater with params: %s" % map(str,params))
    
def end(drawing,params,internal_state) :
    log.info("Ending drawing")
    
def get_params() :
    return  [ 
        {"name":"Ydiv", "default": 12, "description":"divide paper into y divs" },
        {"name":"Xdiv", "default": 12, "description":"divide paper into x divs" },
        {"name":"Total_time", "default": 1440, "description":"time it takes to complete the drawing once" },
        {"name":"Flip", "default":0, "description":"flip every other shape" },
        { "name":"In Min", "default": 1, "description":"Expected input minimum" }, 
        { "name":"In Max", "default": 100, "description":"Expected input maximum" }, 
        { "name":"Out Min", "default": 0.5, "description":"Scaling when input is minimum" }, 
        { "name":"Out Max", "default": 2, "description":"Scaling when input is maximum" }, 
        { "name":"Shape Size", "default": 100, "description":"width of svg shape (px)" }, 
        {"name":"Shape", "default": 'blob.svg', "description":"which svg to use for repeating pattern", 'data_type':"text" }, 
            ]

def get_name() : return "Repeater"
def get_description() : return "every (x minutes place an SVG path on the picture. It will be scaled depending on aggregate sum of data. Option to horizontally flip every other shape"

def can_run(data,params,internal_state):
    last_cell_index = internal_state.get("last_cell",0)
    for point in data.get_current():
        cell_index = get_division(point.date, params)
        if cell_index != last_cell_index:
            log.debug("resetting aggregate as cell index has changed to %d" % cell_index)
            log.debug("repeater can run")
            return True
    return False

