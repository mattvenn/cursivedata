
def process(data,state) :
	print "Example Processing data with",map(str,state.generatorstateparameter_set.all())
	return "Example Changing Processing data with"+str.join("",map(str,state.generatorstateparameter_set.all()))

