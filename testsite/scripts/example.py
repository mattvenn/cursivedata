import pysvg.text

def process(svg_document,data,params,internal_state) :
    #print "Example Processing data with parameters",map(str,params)
    #print "Example internal state: ",internal_state
    #print "Internal State: ",internal_state.get("i","None")
    it = internal_state.get("i",1) + 1
    
    svg_document.addElement(pysvg.text.text("GenRun", x = 50, y = 10))
    for point in data.get_current():
        xp = ((it)%10+0)*10
        yp = ((it)/10+0)*10 
        w = ((float(point['value'])/34000.0))*10/2
        wp = str(w)+"%"
        build = pysvg.builders.ShapeBuilder()
        svg_document.addElement(build.createRect(str(xp)+"%", str(yp)+"%", width="10%", height="10%", fill = "rgb(200, 200, 200)"))
        svg_document.addElement(build.createCircle(str(xp+5)+"%", str(yp+5)+"%", r=wp, fill = "rgb(255, 0, 0)"))
        it = it+1
    internal_state["i"]=it
    return None

def get_params() :
    return  [ { "name":"Width" }, { "name":"Height" } ]

def get_name() : return "Example Generator"
def get_description() : return "Description of Example Generator"

def can_run(data,params,internal_state):
    return len(data.get_current()) >= 2