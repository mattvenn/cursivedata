import math

def polar_to_rect(width, a, c):
    b = width
    gamma = math.acos((a*a+b*b-c*c)/(2.0*a*b))
    y = math.sin(gamma) * a
    x = math.cos(gamma) * a
    return(x,y)

def rect_to_polar(width,x,y):
    l = math.sqrt(pow(x,2)+pow(y,2))
    r = math.sqrt(pow((width-x),2)+pow(y,2))
    return(l,r)

def calculate_distance(x1,y1,x2,y2):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     return dist

