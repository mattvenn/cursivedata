#!/usr/bin/env python
import json
import subprocess
fh=open("history.json")
d=json.load(fh)
generator_dir = "../generators/tree/"
tmp_dir = "../tmp/75479/"
generator = "tree.py"
line_num = 0
for datum in d["power-in"]:
  print datum['at'],datum['value']
  val = int(float(datum['value']))
  
  gen_args = [generator_dir + generator, "--env", str(val), "--number", str(line_num), "--height", "400", "--width", "400", "--dir", tmp_dir ]
  if line_num == 0:
    gen_args.append( "--wipe" )
  print gen_args
  result = subprocess.call(gen_args)
  line_num += 1
