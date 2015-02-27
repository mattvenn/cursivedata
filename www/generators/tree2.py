"""
bugs:
"""
from django.utils.datetime_safe import datetime
from pysvg.builders import *
import pysvg.structure
import math
import random
    
svg_width = 800
ball_width = 15
grid = 21
tree_width = 445

def get_minute(date):
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    mins =  (minute + hour * 60)
    return mins

def process(drawing,data,params,internal_state) :
    aggregate = 0
    minute = int(internal_state.get("minute",0))
    interval = int(params.get("interval",10))

    for point in data.get_current():
        current_minute = get_minute(point.date) 
        aggregate += float(point.getValue())
        print "aggregate:", aggregate
        print "current minute", current_minute
        print "minute + interval", minute + interval
        #if we've got enough time & aggregate to draw a leaf
        if (current_minute > (minute + interval)) and aggregate > 0:

            scale = float(params.get("value",1))
            draw_ball_in_pos(drawing,internal_state,aggregate/scale)

            #reset
            aggregate = 0
            minute = current_minute
        
    internal_state["minute"] = minute

    return None

def draw_ball(drawing,x,y,ball_num):
    w = 310.0 # don't know why I can't calculate this but it's not working
    xscale = w / (grid - 1) # = 15.5
    yscale = xscale
    xoffset = ( drawing.width - w ) / 2 
    yoffset = xoffset

    #draw_ball(drawing,x*xscale+xoffset,y*yscale+yoffset,ball_num)
    x = x*xscale+xoffset
    y = y*yscale+yoffset

    ballsvg = drawing.load_svg("media/tree2/balls/ball_%d.svg" % ball_num)
    ball = ballsvg.getElementAt(1)
    th=TransformBuilder()
    width = drawing.width / svg_width
    offset = ball_width * width / 2

    #doesn't matter what order we put these in, trans happens first so we need to take into account the scaling that happens after
    th.setTranslation("%d,%d" % (x - offset, y-offset))
    th.setScaling(width) 
    ball.set_transform(th.getTransform())
    drawing.doc.addElement(ball)

def get_prob_grid():
    #21 x 21
    return [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,2,0,0,0,3,0,0,0,0,0,0,0,0,],
        [0,0,0,3,1,0,0,3,0,2,1,0,0,1,0,0,0,1,0,0,0,],
        [0,0,0,2,3,1,0,1,1,0,0,1,2,2,0,2,0,3,0,0,0,],
        [0,1,1,2,1,0,0,1,2,0,1,0,1,0,2,3,0,1,0,0,0,],
        [0,0,0,1,3,0,1,0,0,3,0,0,0,3,1,0,0,0,0,0,0,],
        [0,1,2,0,0,2,0,0,1,0,2,3,1,0,0,1,0,1,2,2,0,],
        [0,0,0,0,1,0,1,3,1,1,3,0,0,1,1,0,3,2,3,0,0,],
        [0,0,1,3,0,1,0,0,0,1,0,1,0,3,2,0,0,3,0,0,0,],
        [0,1,3,1,2,0,0,1,0,2,0,3,1,0,1,0,2,0,1,0,0,],
        [0,0,0,2,1,0,2,0,3,0,1,0,0,0,0,1,0,2,0,0,0,],
        [0,0,0,0,0,1,0,1,2,0,0,1,0,3,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,],
        [0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,2,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]]

#test routine to check balls in correct place
def draw_all_balls(drawing):
    prob_grid = get_prob_grid()
    for x in range(grid):
        for y in range(grid):
            ball_num = prob_grid[y][x]
    #        print("%d,%d" % (x*xscale+xoffset,y*yscale+yoffset))
            if ball_num:
                draw_ball(drawing,x,y,ball_num)


def store_starting_probs(internal_state):
    prob_grid = get_prob_grid()
    internal_state["probs"] = [[],[],[]]
    for x in range(grid):
        for y in range(grid):
            ball_num = prob_grid[y][x]

            if ball_num > 0:
                internal_state["probs"][ball_num-1].append([x,y])

def draw_ball_in_pos(drawing,internal_state,size):
    size = int(size)
    #limit size for the number of ball svgs we have
    if size > 2:
        size = 2
                
    #get the random position
    probs = internal_state["probs"]
    #probs contains 3 levels of where we want to draw balls from most (2) to least (0) desired
#    import ipdb; ipdb.set_trace()
    for p in range(2,-1,-1):
        if len(probs[p]):
            (x,y) = random.choice(probs[p])
            #get rid of it
            probs[p].remove([x,y])
            draw_ball(drawing,x,y,size+1)
            break
    else:
        print("ran out of positions to draw in!")


    
   # for (x,y) in internal_state["probs"][ball_num]:
   #     draw_ball(drawing,x,y,ball_num+1)
    
def begin(drawing,params,internal_state) :
    print "Starting tree: ",map(str,params)
    """
    internal_state["last_length"]= [0 for i in range(divs)]
    internal_state["last_div"]= 0
    internal_state["last_val"] = 0
    internal_state["start"] = 1
    """
    store_starting_probs(internal_state)
    tree = drawing.load_svg("media/tree2/tree/tree.svg")
    #after importing, the svg has lost units. Original was 500 px wide, so now 500 units (in this case mm)
    tr=TransformBuilder()
    width =  drawing.width / svg_width
    tr.setScaling( width ) 
    #have to add as a group, or pysvg adds a whole new svg into the drawing
    group = pysvg.structure.g()
    group.set_transform(tr.getTransform())

    for e in tree.getAllElements():
        group.addElement(e)
    drawing.doc.addElement(group)
#    write_scale(drawing,params)
#    draw_balls(drawing)
    """
    draw_ball(drawing,0,0,1);
    draw_ball(drawing,250,250,1);
    draw_ball(drawing,500,500,2);
    """
#    for i in range(50):
#        draw_ball_in_pos(drawing,internal_state,2)
#    draw_all_balls(drawing)
    
def end(drawing,params,internal_state) :
    pass
    #print "Ending drawing with params:",map(str,params)
    #content="Ended at " + str(datetime.now())
    #drawing.bl_text(content,stroke="red",size=15)
    
def write_scale(drawing,params):
    draw_leaf(drawing,10,drawing.height - 100,0,1)
    #assume we get something every 5 minutes - wrong assumption but for now
    #the number we get in is in watts, eg 100 = 100W
    #so if scale is 100, 100W will result in leaf being scaled to 1(original  size)
    #so a full size leaf is equal in energy to 100W for 5min
    #typical is in hours, so divide by (60/5) 12 = 100/12 = 8.3wH
    #if it was 100W but scale is 50, then a full size leaf is 50W for 5 mins
    #so leaf is 50/20 = 2wH
    #so scale text is args.scale/12
    scale_text = "= %.1fWh" % ( params.get("value") / 12 )
    drawing.text(scale_text,50,drawing.height-60,20)

def get_params() :
    return  [ 
        #changing this needs to update the internal state, as we store an array of this number
        {"name":"value", "default":1, "description":"an input value of this will draw a leaf the same size as the scale leaf" },
        {"name":"interval", "default":10, "description":"how long (minutes) to wait before drawing a new leaf" },
            ]

def get_name() : return "Tree"
def get_description() : return "draws a tree, then leaves on the tree "

def can_run(data,params,internal_state):
    minute = int(internal_state.get("minute",0))
    interval = int(params.get("interval",10))
    for point in data.get_current():
        current_minute = get_minute(point.date) 
        if current_minute > minute + interval:
            print "leaf can run, %d > %d + %d" % (current_minute, minute, interval)
            return True
    print "leaf not running"
    return False

