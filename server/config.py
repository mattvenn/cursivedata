
config = {
    46756 :
    {
        "name" : "Bristol Hackspace Light Level",
        "draw_args" : ["--rotate", "0" ],
        "generator" : "../generators/squares/squares.py",
        "needs_polar" : True,
    },
    75479 :
    {
        "name" : "Solar Tree",
        "draw_args" : [ "--scale", "100", "--debug", '--height', '500', '--width', '500'],
        "start_daily" : True,
        "generator" : "../generators/tree/tree.py",
        "needs_polar" : False,
    },
}
        
       
