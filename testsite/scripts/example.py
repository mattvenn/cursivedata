import pysvg.text
import colorsys

def process(svg_document,data,params,internal_state) :
    print "Example Processing data with parameters",map(str,params)
    #print "Example internal state: ",internal_state
    #print "Internal State: ",internal_state.get("i","None")
    it = internal_state.get("i",0) 
    
    for point in data.get_current():
        num = int(params.get("Number",6))
        cell_width = (100.0/num)
        cws = str(cell_width)+"%"
        xp = ((it)%num)*cell_width
        yp = (((it)/num)%num)*cell_width
        w = ((float(point['value'])/34000.0))*cell_width/2
        wp = str(w)+"%"
        hue = float(point['value'])/34000.0
        sat = params.get("Saturation",1.0)
        lev = params.get("Level",0.5)
        rgb = colorsys.hsv_to_rgb(hue, sat, lev)
        rgbs = 'rgb('+str(int(rgb[0]*255.0))+','+str(int(rgb[1]*255.0))+','+str(int(rgb[2]*255.0))+')'
        print "RGB:",rgb
        print "RGBs:",rgbs
        build = pysvg.builders.ShapeBuilder()
        svg_document.addElement(build.createRect(
            str(xp)+"%", str(yp)+"%", width=cws, height=cws, fill="none", stroke="grey", strokewidth=1) )
        svg_document.addElement(build.createCircle(str(xp+cell_width/2)+"%", str(yp+cell_width/2)+"%", r=wp, fill=rgbs))
        it = it+1
    internal_state["i"]=it
    return None

def get_params() :
    return  [ 
             { "name":"Number", "default": 10, "description":"The number of outputs to have horizontally and vertically" }, 
             { "name":"Saturation", "default":0.6, "description":"Saturation of the colour (0-1)" },
             {"name":"Level", "default": 0.9, "description":"Brightness of the colour (0-1)" }, 
             {"name":"Width", "default": 200, "description":"width in mm" },
             {"name":"Height", "default": 200, "description":"height in mm" }, ]

def get_name() : return "Example Generator"
def get_description() : return "Description of Example Generator"

def can_run(data,params,internal_state):
    return len(data.get_current()) >= 2
