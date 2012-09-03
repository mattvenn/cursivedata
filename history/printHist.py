#!/usr/bin/python
import json
fh=open("history.json")
d=json.load(fh)
for line in d:
    print line["at"], line["value"]
