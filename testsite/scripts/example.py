
def process(data,state) :
	print "Example Processing data with",map(str,state.generatorstateparameter_set.all())
	return "Example Changing Processing data with"+str.join("",map(str,state.generatorstateparameter_set.all()))

def get_params() :
	return  [ { "name":"Width" }, { "name":"Height" } ]

def get_name() : return "Example Generator"
def get_description() : return "Description of Example Generator"
