#!/usr/bin/python
import json
import subprocess
fh=open("history.json")
d=json.load(fh)
generator_dir = "../generators/tree/"
generator = "tree.py"
line_num = 0
for datum in d["power-in"]:
  print datum['at'],datum['value']
  val = int(float(datum['value']))

  line_num += 1
  gen_args = [generator_dir + generator, "--env", str(val), "--number", str(line_num), "--height", "500", "--width", "500", "--dir", generator_dir]
  print gen_args
  result = subprocess.call(gen_args)
