
import cursivelib.svg as svg
import re
import json
from pprint import pprint
import os.path

import logging
log = logging.getLogger('graphics')

class RobotSpec() :
    def __init__(self,width,height,top_margin,side_margin):
        self.width = width
        self.height = height
        self.top_margin = top_margin
        self.side_margin = side_margin
        self.img_width = self.width - self.side_margin * 2
        self.img_height = self.height - self.top_margin
        self.x_min = self.side_margin
        self.y_min = self.top_margin
        self.x_max = self.side_margin + self.img_width
        self.y_max = self.top_margin + self.img_height

    def write_outline_gcode(self,filename):
        f = open(filename,'w')
        f.write("g%.1f,%.1f\n" % ( self.side_margin, self.top_margin ))
        f.write("g%.1f,%.1f\n" % ( self.width - self.side_margin , self.top_margin ))
        f.write("g%.1f,%.1f\n" % ( self.width - self.side_margin , self.height ))
        f.write("g%.1f,%.1f\n" % ( self.side_margin , self.height ))
        f.write("g%.1f,%.1f\n" % ( self.side_margin, self.top_margin ))
        f.close()

    def write_calibration_gcode(self,filename):
        f = open(filename,'w')
        f.write("c\n")
        f.close()

    def show(self):
        return "Robot: Width: %d, Height: %d, TopMargin: %d, SideMargin: %d" % (self.width,self.height,self.top_margin,self.side_margin)
    

    # Returns an SVG object in drawing coords, sized to the full printing area
    def svg_drawing(self) :
        return svg.create_svg_doc(self.img_width,self.img_height)

    # Returns an SVG object representing the whole area, including margins
    def svg_total(self) :
        return svg.create_svg_doc(self.width,self.height)

# Expects a string with height,width,topmargin, sidemargin
def string_to_spec(details) :
    nums = re.compile( "^(\\d+),(\\d+),(\\d+),(\\d+)$")
    m = nums.match(details)
    if m:
        print "got data: ", m.group(1),", ",m.group(2),", ",m.group(3),", ",m.group(4)
        return RobotSpec(float(m.group(1)),float(m.group(2)),float(m.group(3)),float(m.group(4)))
    else:
        print "Coudln't parse robot spec: ",details
            
def config_to_spec(filename) :
    if os.path.isfile(filename) :
        log.info("Loading bot spec from file %s" % filename )
    else :
        log.error("Config file not found: %s" % filename )
    with open(filename) as data_file:    
        data = json.load(data_file)
        return RobotSpec( data["width"],data["height"],data["top_margin"],data["side_margin"] )

# Adds in all the different ways of specifying bot setup to the parser's arguments
def add_botspec_arguments(parser) :
    parser.add_argument('--bot_width',
        action='store', dest='bot_width', type=int, 
        help="total overall width of the bot's drawing area")
    parser.add_argument('--bot_height',
        action='store', dest='bot_height', type=int,
        help="total overall height of the bot's drawing area")
    parser.add_argument('--top_margin',
        action='store', dest='bot_top_margin', type=int, 
        help="top margin of the bot's drawing area")
    parser.add_argument('--side_margin',
        action='store', dest='bot_side_margin', type=int,
        help="side margin of the bot's drawing area")
    parser.add_argument('--bot_spec',
	action='store', dest='bot_spec', type=str, 
	help="Robot spec as height, width, top_margin, side_margin")
    parser.add_argument('--bot_config_file',
        action='store', dest='bot_config_file', type=str, 
        help="side margin of the bot's drawing area")

# Tries to find a valid bot spec from all of the parser's arguments
def get_botspec_from_args(args) :
    if args.bot_width and args.bot_height and args.bot_top_margin and args.bot_side_margin :
        log.info("Getting bot from command line parameters")
        return RobotSpec(args.bot_width,args.bot_height,args.bot_top_margin,args.bot_side_margin )
    elif args.bot_spec :
        log.info("Getting bot from command line bot spec (width,height,top,side")
        return string_to_spec(args.bot_spec)
    elif args.bot_config_file :
        return config_to_spec(args.bot_config_file)
    elif os.path.isfile("config") :
        return config_to_spec("config")
    else :
        log.error("Need either: bot_height/width etc. OR bot_spec OR bot_config_file OR for a config file called 'config' to exist")
        


