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

def vect_to_rect(len, angle):
    x = len * math.cos(math.radians(angle))
    y = len * math.sin(math.radians(angle))
    return x, y
    
# nieve calculation for now
# returns 1 for full speed, 0 for stop
def calculate_speed(diff):
    if diff > 90:
        diff = 90
    speed = 1 - (diff / 90.0)
    speed *= 0.8
    return speed

def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def length(v):
  return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
  return math.degrees(math.acos(dotproduct(v1, v2) / (length(v1) * length(v2))))

