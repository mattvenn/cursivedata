import math
from conf import conf

def polar_to_rect(a, c):
    b = conf['width']
    gamma = math.acos((a*a+b*b-c*c)/(2.0*a*b))
    y = math.sin(gamma) * a
    x = math.cos(gamma) * a
    return(x,y)

def rect_to_polar(x,y):
    width = conf['width']
    l = math.sqrt(pow(x,2)+pow(y,2))
    r = math.sqrt(pow((width-x),2)+pow(y,2))
    return(l,r)

def rect_speed_to_polar_speed(x,y,last_x,last_y):
    l,r = rect_to_polar(x,y)
    l_last, r_last = rect_to_polar(last_x,last_y)
    return l - l_last, r - r_last
