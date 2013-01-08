
def process(data,params,internal_state) :
    print "Example Processing data with parameters",map(str,params)
    print "Example internal state: ",internal_state
    print "Internal State: ",internal_state.get("i","None")
    it = internal_state.get("i",0) + 1
    internal_state["i"]=it
    print "Data: ", data.get_current()
    return "Process Iteration "+str(it)

def get_params() :
    return  [ { "name":"Width" }, { "name":"Height" } ]

def get_name() : return "Example Generator"
def get_description() : return "Description of Example Generator"

def can_run(data,params,internal_state):
    return True