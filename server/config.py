
config = {
    46756 :
    {
        "name" : "Bristol Hackspace Light Level",
        "draw_args" : ["--rotate", "20", "--value", "5" ],
        #for the prototype board, force_store makes the robot use the sd card
        "process_args" : ["--width", "200", "--height", "200", "--robot-width", "520", "--robot-height", "300", "--top-margin", "61", "--side-margin", "105", "--force_store" ],
        "generator" : "../generators/squares/squares.py",
        "needs_polar" : True,
    },
    75479 :
    {
        "name" : "Solar Tree",
        "draw_args" : [ "--scale", "100", "--debug", '--height', '400', '--width', '400'],
        "start_daily" : True,
        "generator" : "../generators/tree/tree.py",
        "needs_polar" : False,
    },
}
        
       
