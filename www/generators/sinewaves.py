from django.utils.datetime_safe import datetime
import math


def process(drawing,data,params,internal_state) :
    print "Example Processing data with parameters",map(str,params)
    
    #Read in parameters
    index = internal_state.get("index",0) 
    max = params.get("Data Max",100)
    min = params.get("Data Min",100)
    
    #Run through all the data points
    for point in data.get_current():
        index = index + 1
        initial = float(point.data['value'])
        val = ( initial-min)  / ( max - min )
        print "Data value",val
        draw_wave(drawing,params,val,index)
        
    #Write back any state we want to keep track of
    internal_state["index"]=index 
    return None

def draw_wave(drawing,params,datapoint,index) :
    res = params.get("Resolution",1000)
    amp = ( params.get("Amplitude",0.1) * drawing.height ) * ( 1 + params.get("Amplitude Modulation",0) * datapoint ) 
    freq = ( params.get("Frequency") * 2 * math.pi ) * ( 1 + params.get("Frequency Modulation",0) * datapoint ) 
    phase = ( params.get("Phase",0) * 2 * math.pi ) * ( 1 + params.get("Phase Modulation") * datapoint ) 
    offset = ( params.get("Offset",0.05) * drawing.height * index ) +  (params.get("Offset Modulation",0) * datapoint)
    xprev = None
    yprev = None
    for xind in range(1,res) :
        x = float(xind)/res
        y = amp * math.sin( freq * ( x + phase ) ) + offset
        if xprev :
            drawing.line(xprev * drawing.width,yprev,x*drawing.width,y)
        xprev = x
        yprev = y

def begin(drawing,params,internal_state) :
 #   print "Starting example drawing with params: ",map(str,params)
  #  drawing.tl_text("Started at " + str(datetime.now()),fill="blue",size=15)
    pass
    
def end(drawing,params,internal_state) :
  #  print "Ending exmaple drawing with params:",map(str,params)
   # content="Ended at " + str(datetime.now()) + " after drawing " + str(internal_state.get("i",0)) + " updates"
    #drawing.bl_text(content,fill="red",size="30")
    pass
    
def get_params() :
    return  [ 
             { "name":"Data Max", "default": 1000, "description":"Maximum expected data value" }, 
             { "name":"Data Min", "default": 0, "description":"Minimum expected data value" }, 
             { "name":"Resolution", "default": 1000, "description":"The number of line segments across the drawing" }, 
             { "name":"Resolution", "default": 1000, "description":"The number of line segments across the drawing" }, 
             { "name":"Amplitude Modulation", "default": 0, "description":"How much does the incoming data affect Amplitude of waves" }, 
             { "name":"Frequency Modulation", "default": 0, "description":"How much does the incoming data affect Frequency of waves" }, 
             { "name":"Phase Modulation", "default": 0, "description":"How much does the incoming data affect Phase of waves" }, 
             { "name":"Offset Modulation", "default": 0, "description":"How much does the incoming data affect Offset of waves" }, 
             { "name":"Amplitude", "default": 0.1, "description":"Base size of waves as a proportion of the drawing" }, 
             { "name":"Phase", "default": 0.1, "description":"Offset of the wave relative to the document" }, 
             { "name":"Frequency", "default": 0.1, "description":"How many waves fit across the drawing" }, 
             { "name":"Offset", "default": 0.1, "description":"What proportion of the drawing is between each line" } 
             ] 

def get_name() : return "Example Generator"
def get_description() : return "Description of Example Generator"

def can_run(data,params,internal_state):
    return True;