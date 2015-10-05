import math
import sys
#width of gap between spindles
w = float(sys.argv[1])
#w = 7.0
#diameter of inner spool
d = 22.0
#diameter of string
sd = 0.7
#outer diameter including string, changes as it turns
sr = d
#string length
l = 0

steps_per_m = 34000
steps = 0
turns_per_m = 1000 / (math.pi * d)
fudge =1.9 #make up for string not packing exactly spherical
steps_per_turn = steps_per_m / turns_per_m
pack_d = math.sqrt((3*(sd*sd))/4)
#print(steps_per_turn)
#print(turns_per_m)
loops_per_width = w / sd
loop_num = 0
for turns in range(110):
    loop_num += 1
    steps += steps_per_turn
    if turns % 2 == 0:
        loops_correct = 0
    else:
        loops_correct = 1
    if loop_num > loops_per_width - loops_correct:
        loop_num = 0
        sr += pack_d * fudge
    l = math.pi * turns * pack_d * 2
    #if steps > steps_per_m:
    if turns % 5 == 0:
#        print("steps=%02d turns=%02d spool d=%02.1f string l=%02.1f" % (steps_per_turn*turns,turns, sr, l))
        print("%d,%.1f" % (steps_per_turn*turns,sr))
        steps = 0
