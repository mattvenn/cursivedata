
config = {
    146756 :
    {
        "name" : "Bristol Hackspace Light Level",
        "draw_args" : ["--rotate", "20" ],
        "generator" : "../generators/squares/squares.py",
        "needs_polar" : True,
    },
    46756 :
    {
        "name" : "Solar Tree",
        "draw_args" : [ "--scale", "500", "--debug", "--dir", "../tmp/46756/" ],
        "start_daily" : True,
        "generator" : "../generators/tree/tree.py",
        "needs_polar" : False,
    },
}
        
       
