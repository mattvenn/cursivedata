'''
Created on 2 Feb 2013

@author: dmrust
'''
import pysvg
import colorsys

class Drawing:
    doc = None
    shapes = pysvg.builders.ShapeBuilder()
    def __init__(self, document):
        self.doc = document
        self.width = float(str(self.doc.get_width()).replace("mm",""))
        self.height = float(str(self.doc.get_height()).replace("mm",""))
    
    #Turns an array of floats in [0..1] into an RGB colour string
    def rgb_to_color(self,rgb):
        return 'rgb('+str(int(rgb[0]*255.0))+','+str(int(rgb[1]*255.0))+','+str(int(rgb[2]*255.0))+')'
    
    def hsv_to_color(self,hue, sat, lev):
        rgb = colorsys.hsv_to_rgb(hue, sat, lev)
        return self.rgb_to_color(rgb)
    
    def rect(self,x,y,width,height,fill="none",stroke="grey", strokewidth=1):
        self.doc.addElement(self.shapes.createRect(
            self.dc(x), self.dc(y), width=self.dc(width), height=self.dc(height), fill=fill, stroke=stroke, strokewidth=strokewidth) )
    
    def circle(self,x,y,radius,fill="none",stroke="grey"):
        self.doc.addElement(self.shapes.createCircle(self.dc(x), self.dc(y), r=self.dc(radius), fill=fill, stroke=stroke))
    
    #Takes a number, and turns it into document coordinates. At the moment, just makes a string, but could e.g. add "mm" if necessary
    def dc(self,coord):
        return str(coord)
