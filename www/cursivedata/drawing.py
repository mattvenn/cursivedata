'''
Created on 2 Feb 2013

@author: dmrust
'''
import pysvg
import colorsys
import pysvg.text as txt
from pysvg.parser import parse
from pysvg.shape import *
import math

class Drawing:
    doc = None
    shapes = pysvg.builders.ShapeBuilder()
    def __init__(self, document):
        self.doc = document
        self.width = float(str(self.doc.get_width()).replace("mm",""))
        self.height = float(str(self.doc.get_height()).replace("mm",""))
    
    #so all time formats are the same
    def get_time_format(self):
        return "%d/%m/%y"

    #Turns an array of floats in [0..1] into an RGB colour string
    def rgb_to_color(self,rgb):
        return 'rgb('+str(int(rgb[0]*255.0))+','+str(int(rgb[1]*255.0))+','+str(int(rgb[2]*255.0))+')'
    
    def hsv_to_color(self,hue, sat, lev):
        rgb = colorsys.hsv_to_rgb(hue, sat, lev)
        return self.rgb_to_color(rgb)
    
    #Draws a rectangle with the given x,y as top left, and the given height and width
    def rect(self,x,y,width,height,fill="none",stroke="#000", strokewidth=1,transform=None,id=None):
        rect = self.shapes.createRect( self.dc(x), self.dc(y), width=self.dc(width), height=self.dc(height),
                                        fill=fill, stroke=stroke, strokewidth=strokewidth) 
        if transform :
            rect.set_transform( transform )
        if id :
            rect.set_id(id)
        self.doc.addElement( rect )
    
    def circle(self,x,y,radius,fill="none",stroke="#000",transform=None,id=None):
        circ = self.shapes.createCircle(self.dc(x), self.dc(y), r=self.dc(radius), fill=fill, stroke=stroke)
        if transform :
            circ.set_transform( transform )
        if id :
            circ.set_id(id)
        self.doc.addElement( circ )
   
    def line(self,x1,y1,x2,y2,stroke="#000",strokewidth="1"):
        line = self.shapes.createLine(x1,y1,x2,y2,strokewidth,stroke)
        self.doc.addElement(line)

    def text(self,content,x,y,size=10,family="Helvetica",fill="none",stroke="#000",transform=None,id=None):
        text = txt.text(content=content,x=x,y=y,fill=fill,stroke=stroke)
        text.set_font_size(size);
        text.set_font_family(family)
        if transform :
            text.set_transform( transform )
        if id :
            text.set_id(id)
        self.doc.addElement(text)
        
    #Draws text in the top left corner
    def tl_text(self,content,margin=5,size=10,family="Helvetica",fill="none",stroke="#000"):
        self.text(content,margin,margin+size,size=size,family=family,fill=fill,stroke=stroke)
    #Draws text in the top left corner
    def bl_text(self,content,margin=5,size=10,family="Helvetica",fill="none",stroke="#000"):
        self.text(content,margin,self.height-margin,size=size,family=family,fill=fill,stroke=stroke)
    
    def get_grid(self,nx=None,ny=None ):
        return Grid(self,nx,ny)
    
    #Takes a number, and turns it into document coordinates. At the moment, just makes a string, but could e.g. add "mm" if necessary
    def dc(self,coord):
        return str(coord)

    #allows loading external svgs into the drawing
    def import_svg(self,svg_file):
        try:
            svg_parsed = parse(svg_file)
            for e in svg_parsed.getAllElements():
                self.doc.addElement( e )
        except (ExpatError, IOError) as e:
            print "problem parsing %s:%s" % (svg_file,e)
            raise

    def load_svg(self,svg_file):
        svg_parsed = parse(svg_file)
        return svg_parsed

class Grid:
    def __init__(self, drawing, nx=None, ny=None ):
        self.drawing = drawing
        w = drawing.width
        h = drawing.height
        if nx and ny:
            #Figure out scales for both, use smaller, set offset
            #Use nx to set size, and do ny to fit
            self.size_x = min( w/nx, h/ny )
            self.size_y = min( w/nx, h/ny )
            self.nx = math.floor(w/self.size_x)
            self.ny = math.floor(h/self.size_y)
        elif nx:
            #Use nx to set size, and do ny to fit
            self.size_x = w/nx
            self.size_y = w/nx
            self.nx = nx;
            self.ny = math.floor(h/self.size_y)
        elif ny:
            #Use ny to set size, and do nx to fit
            self.size_x = w/ny
            self.size_y = w/ny
            self.nx = math.floor(w/self.size_x)
            self.ny = ny
        self.offset_x = (w - (self.nx * self.size_x ) ) / 2
        self.offset_y = (h - (self.ny * self.size_y ) ) / 2
    
    def index_to_xy(self,i):
        return( i%self.nx,int(i/self.nx)%self.ny )
        
    def cell(self,index):
        x,y = self.index_to_xy(int(index))
        return self.cell_xy(x,y)
    
    #Returns the top left corner of the cell
    def cell_xy(self,x,y):
        return Cell(self.offset_x+x*self.size_x,self.offset_y+y*self.size_y,self.size_x,self.size_y)
    
class Cell:
    def __init__(self, x, y, xsize,ysize ):
        self.x = x;
        self.y = y;
        self.width = xsize;
        self.height = ysize;
    def tl(self):
        return (self.x,self.y)
    def br(self):
        return (self.x+self.width,self.y+self.height)
    def cent(self):
        return (self.x+self.width/2,self.y+self.height/2)
