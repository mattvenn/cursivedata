
def process(data,state) :
	print "Processing data with",map(str,state.generatorstateparameter_set.all())
	return "Processing data with"+str.join("",map(str,state.generatorstateparameter_set.all()))

