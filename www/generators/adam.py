"""
bugs:
  with squareIncMM an odd number, the squares don't join up properly...
"""
from django.utils.datetime_safe import datetime
import math
import logging
log = logging.getLogger('generator')



class Periods:
     def __init__(self, date, params):
        self.date = date
        self.params = params
   
     # 'periods' is an array of minutes that has as many levels of time as we need - e.g. 
     # [10, 60, 1440] would break time up into days (1,440 mins), hours (60 mins), and 10 minute periods; 
     # [15, 90] would break time into periods of 1.5 hours (90 mins) & sub-periods of 15 minutes. 
     # For now we can only handle two periods at a time.
    
     def get_periods(self):
         params = self.params
         periods = []
         periods.append(float(params.get("Period0",60)))
         periods.append(float(params.get("Period1",1440)))
         return periods
        
     def get_num_periods(self):
        periods = self.get_periods()
        num_periods = int( periods[1] / periods[0] )
        return num_periods

     def get_current_periods(self):
         params = self.params
         date = self.date
         periods = self.get_periods()
         num_periods = self.get_num_periods()

         minute = int( date.strftime("%M") ) # minute 0 - 59
         hour = int(date.strftime("%H") ) # hour 0 - 23
         day = int(date.strftime("%-d") ) # day 1 - 31 (- = not zero peadded)
         month = int(date.strftime("%-m")) # month 1-12 (- = not zero peadded)
         year = int(date.strftime("%Y")) # year in four digits (2013)

         current_period1 = ( minute + (hour * 60) ) / periods[1]
         current_period0 = ( ( minute + (hour * 60) ) / periods[0] ) % num_periods
         current_periods = []
         current_periods.append( int(current_period0) ) 
         current_periods.append( int(current_period1) )
         return current_periods


def process(drawing,data,params,internal_state) :
    p = Periods(data.get_current()[0].date, params)

    log.debug("p.get_periods() = %s" % p.get_periods())
    log.debug("p.get_num_periods() = %s" % p.get_num_periods())
    log.debug("p.get_current_periods() = %s" % p.get_current_periods())
    current_periods = p.get_current_periods()
    aggregate = internal_state.get("aggregate",0)
    grid = drawing.get_grid(nx=p.get_num_periods(),ny=params.get("Ydiv"))
    circle = int(params.get("Circle",0))

    for point in data.get_current():
        aggregate += float(point.getValue())
        #allow user to determine how fast the graph is drawn again
        last_periods = current_periods
        point_periods = Periods(point.date, params)
        current_periods = point_periods.get_current_periods()
        #work out where to draw
        cell = grid.cell(current_periods[0] + current_periods[1])
        cx, cy = cell.cent()
       
        log.debug("x:%d y:%d" % (cx, cy))

        #if we have aggregated enough values to draw a square
        log.debug("current_periods = %s, last_periods = %s" % (current_periods, last_periods))
        if current_periods != last_periods :
            width = math.sqrt( aggregate / float(params.get("Value")) )
            hWidth = width / 2
            if width > 1:
                drawing.rect(cx-hWidth,cy-hWidth,width,width,id=id)
        
               
            aggregate = 0
           

    internal_state["aggregate"]=aggregate
    return None

def begin(drawing,params,internal_state) :
    log.info("Starting drawing adams with params: %s" % params)
    drawing.tl_text("Started at " + str(datetime.now()),size=15,stroke="blue")
   
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
        {"name":"Value", "default":10, "description":"value of each square" },
        {"name":"Circle", "default":0, "description":"set to 1 to make circles instead" },
        {"name":"Period1", "default":60, "description":"How many minutes should each ROW of objects represent?" },
        {"name":"Period0", "default":5, "description":"How many minutes should each object represent?" }, 
            ]

def get_name() : return "Test"
def get_description() : return "Test Description"

def can_run(data,params,internal_state):
    last_periods = internal_state.get("last_periods",0)
    for point in data.get_current():
        p = Periods(point.date, params)
        log.debug("point.date = %s" % point.date)
        current_periods = p.get_current_periods() #get_current_periods(point.date, params)
        if current_periods != last_periods:
            log.info("adams can run")
            return True
    return False
