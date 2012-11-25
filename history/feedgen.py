#!/usr/bin/env python
import json
import subprocess
import iso8601
fh=open("history.json")
d=json.load(fh)
generator_dir = "../generators/squares/"
tmp_dir = "../tmp/46756/"
generator = "squares.py"
line_num = 0
for datum in d["light"]:
    print datum['at'],datum['value']
    val = int(float(datum['value']))
    time = datum['at']
    date = iso8601.parse_date(time)
    minute = int( date.strftime("%M") ) # minute 0 -59
    hour = int(date.strftime("%H") ) # hour 0 -23
    day = int(date.strftime("%d") ) # day

    #ten mins
    mins =  (minute + hour * 60)/10 # 0 - 143

    gen_args = [generator_dir + generator, "--value", "1000", "--env", str(val), "--number", str(mins), "--height", "400", "--width", "400", "--dir", tmp_dir ]
    if line_num == 0:
      gen_args.append( "--wipe" )
    print gen_args
    result = subprocess.call(gen_args)
    line_num += 1
